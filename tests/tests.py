import sys
sys.path.insert(0, '..')

from input_new_papers_to_csv import iterate_through_dicts

def test_iterate_through_dicts():
    print("Testing iterate_through_dicts function...")
    test_dict = {
        'Quantum_Mechanics': {
            'Quantum_Computing':[],
            'Quantum_Key_Distribution':[],
            'Quantum_LIDAR': {
                'N00N_States': [],
                'HUP': [],
            }
        },
        'Machine_Learning': {
            'Deep_Learning': {
                'Conv_Nets': [],
                'GANs': []
            }
        }
    }

    indiced_dict = iterate_through_dicts(test_dict)
    print('indiced_dict: ', indiced_dict)


if __name__ == '__main__':
    test_iterate_through_dicts()


