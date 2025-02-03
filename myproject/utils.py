import os

def create_static_folder(base_dir):
    static_dir = os.path.join(base_dir, 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        # print(f"Static folder created at: {static_dir}")
    else:
        print(f"Static folder exists at: {static_dir}")
