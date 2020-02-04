from pprint import pprint
from json import load, dump
from sys import argv
import logging
logging.basicConfig(filename='vcv.log', level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')
debug = logging.debug
debug('\n\n\n')

class Cable(object):
    def __init__(self, data, parent):
        self.raw_data = data
        self.id = data.get('id')
        self.parent = parent
        self.outputModuleId = data.get('outputModuleId')
        self.outputId = data.get('outputId')
        self.inputModuleId = data.get('inputModuleId')
        self.inputId = data.get('inputId')
        self.color = data.get('color')
        self.attached_module_ids = [self.outputModuleId, self.inputModuleId]
        return
    
    def update_cable_id(self, i):
        self.id = i
        self.raw_data['id'] = i

    def check_for_module(self, module_id):
        return module_id in self.attached_module_ids

    def update_module_id(self, module_id_mapping):
        new_out = module_id_mapping[self.outputModuleId]
        new_in = module_id_mapping[self.inputModuleId]
        self.outputModuleId = new_out
        self.raw_data['outputModuleId'] = new_out
        self.inputModuleId = new_in
        self.raw_data['inputModuleId'] = new_in


class Module(object):
    def __init__(self, data, parent):
        self.raw_data = data
        self.id = data.get('id')
        self.plugin = data.get('plugin')
        self.model = data.get('model')
        self.parent = parent
        pos = data.get('pos')
        self.x = pos[0]
        self.y = pos[1]
        return

    def get(self, key):
        return self.raw_data.get(key)

    def update(self, key, value):
        if key in self.raw_data:
            self.raw_data[key] = value

    def get_module_to_right(self):
        right_id = self.raw_data.get('rightModuleId')
        if not right_id:
            return None
        right_module = self.parent.get_module_by_id(right_id)
        return right_module

    def get_all_modules_to_right(self):
        all_modules = [self]
        next_mod = self.get_module_to_right()
        while next_mod:
            all_modules.append(next_mod)
            next_mod = next_mod.get_module_to_right()
        return all_modules

    def get_attached_cables(self):
        cables = []
        for cable in self.parent.cables:
            if cable.check_for_module(self.id):
                cables.append(cable)
        return cables

    def update_pos(self, x, y):
        self.pos = [x, y]
        self.raw_data['pos'] = [x, y]


class Rack(object):
    def __init__(self, filename):
        self.export_names='all'
        if '.vcv.' in filename:
            self.export_names = filename.split('.vcv.')[1].split('.')
            filename = filename.split('.vcv.')[0] + '.vcv'
        self.filename = filename
        self.raw_data = self.read_vcv_file(filename)
        self.version = self.raw_data.get('version')
        self.modules = [Module(snippet, self) for snippet in self.raw_data.get('modules')]
        self.cables = [Cable(snippet, self) for snippet in self.raw_data.get('cables')]
        return

    def read_vcv_file(self, filename):
        with open(filename, 'r') as vcv_file:
            data = load(vcv_file)
        return data

    def get_module_by_id(self, module_id):
        return next((m for m in self.modules if m.id == module_id), None)

    def get_modules_by_name(self, name):
        return [m for m in self.modules if m.model == name]

    def get_starting_blocks(self):
        text_blocks = self.get_modules_by_name('TD-202')
        starting_blocks = [m for m in text_blocks if m.get('text').startswith('EXPORT: ')]
        if self.export_names == 'all':
            debug(f"Exporting all relevant blocks from {self.filename}:")
            debug(f"{[b.get('text') for b in starting_blocks]}")
            return starting_blocks
        wanted_blocks = []
        for export_name in self.export_names:
            export_name = f'EXPORT: {export_name}'
            if export_name not in [m.get('text') for m in starting_blocks]:
                debug(f"Warning: Could not find {export_name} in {self.filename}. Skipping.")
                continue
            debug(f"found {export_name} in {self.filename}.")
            wanted_block = next((m for m in text_blocks if m.get('text') == export_name), None)
            if wanted_block:
                wanted_blocks.append(wanted_block)
        return wanted_blocks


class Export_Block(object):
    def __init__(self, starting_block):
        self.name = starting_block.get('text').replace('EXPORT: ', '')
        starting_block.update('text', self.name)
        self.starting_block = starting_block
        self.modules = starting_block.get_all_modules_to_right()
        self.cables = self.get_internal_cables()
        self.normalize_pos()
        self.module_id_mapping = {}
        return
    
    def all_module_ids(self):
        return [m.id for m in self.modules]

    def normalize_pos(self, y=0):
        start_x = self.starting_block.x
        for module in self.modules:
            module.update_pos(module.x-start_x, y)
        return self

    def make_ids_unique(self, y):
        cable_counter = 0
        for i, module in enumerate(self.modules):
            old_id = module.id
            new_module_id = (y*100) + i
            module.id = new_module_id
            module.update('id', new_module_id)
            self.module_id_mapping[old_id] = new_module_id
        debug(self.module_id_mapping)
        for j, cable in enumerate(self.cables):
            cable.update_module_id(self.module_id_mapping)
            cable_id = (y*1000) + j
            cable.update_cable_id(cable_id)
        return self

    def output_modules(self):
        return [m.raw_data for m in self.modules]
    def output_cables(self):
        return [m.raw_data for m in self.cables]
    
    def get_internal_cables(self):
        cables = set()
        for module in self.modules:
           for cable in module.get_attached_cables():
               if cable.outputModuleId in self.all_module_ids() and cable.inputModuleId in self.all_module_ids():
                   cables.add(cable)
        return list(cables)


if __name__ == "__main__":    
    input_filenames = argv[1:]
    racks = [Rack(filename) for filename in input_filenames]
    starting_blocks = sum([rack.get_starting_blocks() for rack in racks], [])
    export_blocks = [Export_Block(starting_block) for starting_block in starting_blocks]
    [export_block.normalize_pos(i).make_ids_unique(i)  for i, export_block in enumerate(export_blocks)]

    output  = {
        "version": "1.1.5",
        "modules": sum([export_block.output_modules() for export_block in export_blocks], []),
        "cables": sum([export_block.output_cables() for export_block in export_blocks], []),
        }

    with open('test.vcv', 'w') as output_file:
        dump(output, output_file, indent=2)
