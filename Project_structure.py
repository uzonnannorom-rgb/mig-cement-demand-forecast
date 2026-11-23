import os


def create_project_structure(base_dir):
    folders = {
        'data': ['raw', 'processed'],
        'notebooks': [],
        'src': [],
        'artifacts': [],
        'dashboard': [],
        'reports': []
    }

    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
        print(f'Created base directory: {base_dir}')

    for main_folder, sub_folders in folders.items():
        main_folder_path = os.path.join(base_dir, main_folder)
        if not os.path.exists(main_folder_path):
            os.mkdir(main_folder_path)
            print(f'Created main folder: {main_folder_path}')

        for sub_folder in sub_folders:
            sub_folder_path = os.path.join(main_folder_path, sub_folder)
            if not os.path.exists(sub_folder_path):
                os.mkdir(sub_folder_path)
                print(f'Created sub-folder: {sub_folder_path}')

    print('Project folder structure created successfully')


script_folder = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.join(script_folder, 'mig-cement-demand-forecast')

create_project_structure(base_directory)