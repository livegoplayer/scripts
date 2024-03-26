import os

mirror_url = "https://hf-mirror.com"
os.environ['HF_ENDPOINT'] = mirror_url
os.environ['NO_PROXY'] = 'localhost, 127.0.0.1, ::1, ip.cn, chinaz.com, 192.168.0.0/16, mirrors.cloud.aliyuncs.com, hf-mirror.com, lfs.huggingface.co, hf-hub-lfs-us-east-1.s3-accelerate.amazonaws.com'
# os.environ["HTTP_PROXY"] = ""
# os.environ["HTTPS_PROXY"] = ""

import subprocess
import json
from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError, RepositoryNotFoundError, RevisionNotFoundError
from huggingface_hub.hf_api import RepoFile, RepoFolder
from cryptography.fernet import Fernet

import re
import json
from datetime import datetime

# Specify the mirror URL

raw_url = "https://huggingface.co"

user=""
user_id=""
api=None
id_mapping = {}
repo_types = {}
commit_message = ""
current_project = ""
current_project_repo_type = ""

# 避免明文被捕捉到
def get_defalut_access_token():
    # todo 
    # 生成密钥
    key = b'DHeLgM3wzjOUOmmALgijDFX5z95bKXsPcbrt2CsrhiY='
    cipher = Fernet(key)

    # 需要加密的数据
    token_encode = b'gAAAAABmAEySz9SvSPu7N1VwS4ag7rRjxRPGgVSpyV5jD_pRt-CQcmBOPd-qcOBQdRDmmg3SV0mK_kHtjypyYX1IK6bXYR5lGM_ABVyIzs4sDAjC3PFg9QYqUF_rEG5PTXaIRQdi47JY'

    # 解密数据
    decrypted_token = cipher.decrypt(token_encode)
    return decrypted_token.decode('utf-8')

def save_access_token(access_token):
    """保存 AccessToken 到文件中."""
    with open("access_token.json", "w") as f:
        json.dump({"access_token": access_token}, f)

def load_access_token():
    """加载保存的 AccessToken."""
    try:
        with open("access_token.json", "r") as f:
            return json.load(f)["access_token"]
    except FileNotFoundError:
        return None

def login(init=False):

    """登录到 Hugging Face 账户. 只有初始化的时候才可以略过登录，直接读取本地文件，其他情况代表手动调用"""
    access_token = load_access_token()
    if not (access_token and init):
        print("检测到你是第一次登录，请选择模式(这个页面只会显示一次，如果想要再次进入请删除脚本目录下的access_token.json)：")
        print("1. 登录自己的access_token(可以登录huggingface设置里面新建一个，这样的话管理的就是你自己的账号)")
        print("2. 使用公共账号(程序作者使用小号创建的access_token,宗旨是让大家一起管理这个账号)")
        choice = input("请输入你的选择：")
        if choice == "1":
            access_token = input("请输入您的 AccessToken: ")
            save_access_token(access_token)
        elif choice == "2":
            access_token = get_defalut_access_token()
            save_access_token(access_token)
        else:
            print("无效的操作编号，请重新输入")

    access_token = load_access_token()
    subprocess.run(["huggingface-cli", "login", "--token", access_token], capture_output=True, text=True)

    return access_token

def makesure_login(init=False):
    global user, api, user_id

    if init:
        login(init)

    """确保登录成功."""
    while True:
        status, res = check_login()
        if status:
            print(f"登录成功，用户名为: {res}")
            if api == None:
                api = HfApi(endpoint=mirror_url, token=load_access_token())
                user=res
                user_id = user
            break
        else:
            print(f"登录失败，请重新登录, {res}")
            login(init)


def check_login():
    result = subprocess.run(["huggingface-cli", "whoami"], capture_output=True, text=True)

    if result.returncode == 0:
        return True, result.stdout.split("\n")[0]
    else:
        return False, result.stderr

def get_start_end_num():
    """获取 id_mapping 中的最小和最大数字 id."""
    global id_mapping
    if not id_mapping:
        return None, None
    
    min_id = min(id_mapping.values())
    max_id = max(id_mapping.values())
    return min_id, max_id

def list_models():
    """列出所有模型."""
    global id_mapping, repo_types
    models = api.list_models(author=user, token=load_access_token())
    print("\nModels:")
    print("| {:<5} | {:<40} | {:<30} | {:<20} | {:<10} |".format("ID", "Model ID", "Created At", "Type", "Private"))
    print("| {:<5} | {:<40} | {:<30} | {:<20} | {:<10} |".format("-"*5, "-"*40, "-"*30, "-"*20, "-"*10))
    for i, model in enumerate(models, start=1):
        model_id = model.id
        repo_type = repo_types.get(model_id, "model")
        id = get_or_create_id(model_id)
        id_mapping[model_id] = id
        repo_types[model_id] = repo_type
        print(f"| {id:<5} | {model_id.ljust(40)} | {str(model.created_at).ljust(30)} | {repo_type.ljust(20)} | {str(model.private).ljust(10)} |")


def list_datasets():
    """列出所有数据集."""
    global id_mapping, repo_types
    datasets = api.list_datasets(author=user, token=load_access_token())
    print("\nDatasets:")
    print("| {:<5} | {:<40} | {:<30} | {:<20} | {:<10} |".format("ID", "Dataset ID", "Created At", "Type", "Private"))
    print("| {:<5} | {:<40} | {:<30} | {:<20} | {:<10} |".format("-"*5, "-"*40, "-"*30, "-"*20, "-"*10))
    for i, dataset in enumerate(datasets, start=1):
        dataset_id = dataset.id
        repo_type = repo_types.get(dataset_id, "dataset")
        id = get_or_create_id(dataset_id)
        id_mapping[dataset_id] = id
        repo_types[dataset_id] = repo_type
        print(f"| {id:<5} | {dataset_id.ljust(40)} | {str(dataset.created_at).ljust(30)} | {repo_type.ljust(20)} | {str(dataset.private).ljust(10)} |")


def get_or_create_id(repo_id):
    """返回对应 repo_id 的数字 id，如果不存在则创建一个新的数字 id."""
    global id_mapping
    if repo_id in id_mapping:
        return id_mapping[repo_id]
    else:
        new_id = len(id_mapping) + 1
        id_mapping[repo_id] = new_id
        return new_id

def get_repo_type(repo_id):
    """根据 repo_id 获取对应的 repo_type."""
    global repo_types, current_project_repo_type
    t =  repo_types.get(repo_id, "unknown") 
    if t == "unknown":
        return current_project_repo_type
    return t

def list_projects():
    """列出用户的项目列表."""
    makesure_login()
    list_all()
    while True:
        print("\n请选择操作:")
        print("1. list all models")
        print("2. list all datasets")
        print("3. list all")
        print("4. 添加一个新项目")
        # print("5. 下载某个项目")
        print("5. 选择一个项目为当前项目")
        print("6. 返回上一级")
        choice = input("请输入操作编号: ")
        
        if choice == "1":
            list_models()
        elif choice == "2":
            list_datasets()
        elif choice == "3":
            list_all()
        elif choice == "4":
            repo_id = create_repository()
        # elif choice == "5":
        #     download_project()
        elif choice == "5":
            start, end = get_start_end_num()
            select_current_project(start, end)
        elif choice == "6":
            return  # Return to the previous level
        else:
            print("无效的操作编号，请重新输入")

def list_all():
    """列出所有模型、数据集和空间."""
    list_models()
    list_datasets()

def get_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None  # 如果找不到对应的键，返回 None

def select_current_project(start_num, end_num):
    """选择一个项目为当前项目."""
    global current_project, id_mapping, current_project_repo_type
    while True:
        selected_id = input(f"请在 {str(start_num)} - {str(end_num)} 之中选择一个项目编号，或直接输入repo_id作为当前选择的项目: ")
        if selected_id.isdigit() and start_num <= int(selected_id) <= end_num:
            current_project = get_key_by_value(id_mapping, int(selected_id))
            print(f"当前项目: {current_project}")
            show_project_details()
            break
        elif "/" in selected_id:
            current_project = selected_id
            print(f"当前项目: {current_project}")
            if not is_own_project(current_project):
                print("检测到当前项目不是本人的项目，请手动指定库的类型")
                print("1. 模型 (Model)")
                print("2. 数据集 (Dataset)")
                project_type = input("请输入项目类型编号，直接回车返回上一级: ")
                if project_type == "":
                    return
                if project_type == "1":
                    repo_type = None
                elif project_type == "2":
                    repo_type = "dataset"
                else:
                    print("无效的项目类型编号，请重新输入")
                    return
                current_project_repo_type = repo_type
            show_project_details()
            break
        else:
            print("无效的项目编号，请重新选择。")

def show_project_details():
    """显示项目的具体内容，并提供下载和上传文件的选项."""
    global current_project, api
    makesure_login()
    if current_project:
        try:
            # Get project details
            info = api.repo_info(current_project, token=load_access_token(), repo_type=get_repo_type(current_project))
            print(f"项目信息:")
            print(f"ID: {info.id}")
            print(f"Author: {info.author}")
            print(f"Created At: {info.created_at}")
            print(f"Last Modified: {info.last_modified}")
            print(f"Private: {info.private}")
            
            print_tree(current_project)

            # Provide options for downloading or uploading files
            while True:
                print("\n请选择操作:")
                print("1. 下载一个或多个项目文件")
                print("2. 上传一个或多个项目文件")
                print("3. 下载整个项目")
                print("4. 返回上一级")
                choice = input("请输入操作编号: ")
                if choice == "1":
                    download_files(current_project)
                elif choice == "2":
                    upload_files(current_project)
                elif choice == "3":
                    download_project(current_project)
                elif choice == "4":
                    return  # Return to the previous level
                else:
                    print("无效的操作编号，请重新输入。")
        except HfHubHTTPError as e:
            print(f"获取项目详情失败: {e}")
    else:
        print("未选择任何项目。")



def format_size(size):
    """将文件大小格式化为更易读的形式."""
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}B"

def print_tree(repo_id, path=None, expand=False, revision=None, repo_type=None, indent=""):
    """以树状形式打印项目文件结构."""
    global api
    if path is None:
        path = ''
    repo_tree = api.list_repo_tree(repo_id, path, token=load_access_token(), repo_type=get_repo_type(repo_id))
    for item in repo_tree:
        if isinstance(item, RepoFile):
            file_size = format_size(item.size) if item.size else "0 B"
            print(indent + f"📄 {item.path} (Size: {file_size})")
        elif isinstance(item, RepoFolder):
            print(indent + f"📁 {item.path}/")
            print_tree(repo_id, path=f"{item.path}", expand=expand, indent=indent + "   ")

def save_last_folder(folder_path):
    """
    Save the last used folder path to a configuration file.
    If the folder does not exist, create it.
    
    Args:
    - folder_path (str): The folder path to save.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        print(f"文件夹 '{folder_path}' 不存在，已创建。")

    config = {"last_folder": folder_path}
    with open("config.json", "w") as f:
        json.dump(config, f)

def get_default_folder():
    default_folder = os.getcwd()  # 默认文件夹为当前工作目录
    config_file = "config.json"
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
            if "last_folder" in config and os.path.exists(config["last_folder"]):
                default_folder = config["last_folder"]
    return default_folder

def download_files(repo_id):
    total_files = 0
    successful_downloads = 0
    failed_downloads = 0

    while True:
        default_folder = get_default_folder()

        print("\n请输入要下载的文件路径，多个文件请使用逗号分隔, 回车返回上一级")
        file_paths_input = input("请输入文件路径: ")
        if len(file_paths_input) == 0:
            return
        
        folder_path = input(f"请输入本地文件夹路径，按回车使用{default_folder}：")

        if folder_path == "":
            folder_path = default_folder

        save_last_folder(folder_path)

        file_paths = [file_path.strip() for file_path in file_paths_input.split(",")]
        total_files += len(file_paths)

        # Prompt user to place downloaded files in corresponding folders
        user_choice = input("是否把下载的文件放到对应的文件夹？(Y/n)：")
        dir_obj = False
        if user_choice.lower() != 'n':
            dir_obj = True

        for file_path in file_paths:
            # Extract filename and subfolder from file_path
            if "/" in file_path:
                parts = file_path.rsplit("/", 1)
                filename = parts[-1]
                subfolder = parts[0]
            else:
                filename = file_path
                subfolder = ""

            try:
                path_input = folder_path
                if dir_obj:
                    path_input = folder_path + "/" + subfolder
                print(f'downloading {filename} to {path_input}...')
                api.hf_hub_download(repo_id=repo_id, filename=filename, subfolder=subfolder, local_dir=path_input, local_dir_use_symlinks=False, token=load_access_token(), repo_type=get_repo_type(current_project))
                successful_downloads += 1
            except Exception as e:
                print(f"下载文件 '{filename}' 时出错：{e}")
                failed_downloads += 1

        print(f"\n总共下载文件数: {total_files}")
        print(f"成功下载文件数: {successful_downloads}")
        print(f"失败下载文件数: {failed_downloads}")

import os

def upload_files(repo_id):
    """上传一个或多个项目文件."""
    global api
    makesure_login()
    if not is_own_project(repo_id):
        print("检测到当前项目不是本人的项目，故而没有上传权限")
        return
    while True:
        file_paths_input = input("请输入要上传的文件路径(多个文件请用逗号分隔), 回车返回上一级: ")
        if len(file_paths_input) == 0:
            return
        file_paths = [path.strip() for path in file_paths_input.split(",")]

        relative_paths_input = input("请输入要上传的文件相对路径, 没有会自动创建，不填全部上传到根目录(多个路径请用逗号分隔): ")
        if len(relative_paths_input) == 0:
            relative_paths = [""]
        else:
            relative_paths = [path.strip() for path in relative_paths_input.split(",")]

        if len(relative_paths) < len(file_paths):
            fill_choice = input("文件路径数目大于相对路径数目，请选择填充方式：\n1. 使用根目录填充\n2. 根据最后一个路径填充\n请选择(1/2): ")
            if fill_choice == "1":
                relative_paths += ["" for _ in range(len(file_paths) - len(relative_paths))]
            elif fill_choice == "2":
                last_path = relative_paths[-1] if relative_paths else ""
                relative_paths += [last_path for _ in range(len(file_paths) - len(relative_paths))]
        elif len(relative_paths) > len(file_paths):
            ignored_paths = relative_paths[len(file_paths):]
            print(f"文件路径数目小于相对路径数目,以下相对路径将被忽略: {', '.join(ignored_paths)}")
            relative_paths = relative_paths[:len(file_paths)]

        # 获取当前时间
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        default_message = f"{user_id} uploaded at {current_time}"
        commit_message = input(f"请输入本次提交的目的，(回车默认填写:{default_message}):")

        for file_path, relative_path in zip(file_paths, relative_paths):
            # Convert relative path to absolute path
            absolute_path = os.path.abspath(file_path)
            if not os.path.exists(file_path):
                print(f"文件 '{file_path}' 不存在，跳过上传。")
                continue

            try:

                # 构造 commit_message
                if len(commit_message) == 0: 
                    commit_message = default_message
                else: 
                    commit_message = f"{user_id}: " + commit_message
                file_name = os.path.basename(file_path)
                print(f'uploading {absolute_path} to {repo_id}/{relative_path}/{file_name}...')
                #huggingface-cli upload --token hf_*** username/reponame . .
                # os.environ['HF_ENDPOINT'] = mirror_url
                # access_token = load_access_token()
                # res = subprocess.run(["huggingface-cli", "upload", f"--token={access_token}",f"{repo_id}", f"{absolute_path}", f"{relative_path+'/'+file_name}", f"--commit-message=\'{commit_message}\'", f"--repo-type={get_repo_type(current_project)}"], capture_output=True, text=True)
                # print(res)
                # os.environ['HF_ENDPOINT'] = ''

                api.upload_file(repo_id=repo_id, path_or_fileobj=absolute_path, path_in_repo=relative_path + "/"  + file_name, commit_message=commit_message, token=load_access_token(), repo_type=get_repo_type(current_project))
                print(f"文件 {file_path} 上传成功。")
            except HfHubHTTPError as e:
                print(f"文件 {file_path} 上传失败: {e}")
            except ValueError as e:
                print(f"文件 {file_path} 上传失败: {e}")
            except RepositoryNotFoundError as e:
                print(f"文件 {file_path} 上传失败: {e}")
            except RevisionNotFoundError as e:
                print(f"文件 {file_path} 上传失败: {e}")

        break

def is_own_project(repo_id):
    """检查给定的 repo_id 是否为当前用户的项目."""
    global id_mapping
    return repo_id in id_mapping

def create_repository():
    global user, api, id_mapping, repo_types
    makesure_login()
    repo_type=None
    try:
        """添加一个新项目."""
        print("\n请选择要创建的项目类型:")
        print("1. 模型 (Model)")
        print("2. 数据集 (Dataset)")
        project_type = input("请输入项目类型编号，直接回车返回上一级: ")
        if project_type == "":
            return
        
        if project_type == "1":
            repo_type = None
            project_name = input("请输入模型名称, 直接回车返回上一级: ")
        elif project_type == "2":
            repo_type = "dataset"
            project_name = input("请输入数据集名称, 直接回车返回上一级: ")
        else:
            print("无效的项目类型编号，请重新输入")
            return

        if project_name == "":
            return

        private = input("是否为私有库， 请输入 y 或 n: ") == "y"
        # 创建存储库
        api.create_repo(project_name, private=private, repo_type=repo_type, token=load_access_token())

    except HfHubHTTPError as e:
        error_code = extract_first_three_digits(str(e))
        if error_code == 403:
            print("HTTPError 403: You don't have write permissions to the repository.")
        elif error_code == 404:
            print("HTTPError 404: The repository or project doesn't exist on the Hub.")
        elif error_code == 409:
            print("HTTPError 409: The project already exists in the collection and _ok=False.")
        else:
            print(f"HTTPError {e.server_message}")

    except ValueError as e:
        """bug"""
        print("warning:"  + str(e))
    
    repo_id = user + '/' + project_name
    if not private:
        url = mirror_url + "/" + repo_id
    else:
        url = "https://huggingface.co" + "/" + repo_id + " " + "(私有存储库无法在镜像站点上显示)"
    # 检查是否成功创建存储库
    if url:
        print(f"存储库 {repo_id} 创建成功！地址为：" + url)
        id = get_or_create_id(repo_id)
        id_mapping[repo_id] = id
        repo_types[repo_id] = repo_type
    else:
        print("存储库创建失败，请检查权限或存储库是否已存在。")
    return repo_id

def extract_first_three_digits(s):
    match = re.search(r'\d{3}', s)
    if match:
        return int(match.group())
    return 0

def getrepoid_from_url(url):
    parts = url.split('/')
    repo_id = parts[-2] + "/" + parts[-1]
    return repo_id

def download_project(repo_id):
    """下载某个项目."""
    # Your code to download a project goes here
    default_folder = get_default_folder()

    folder_path = input(f"请输入文件夹路径，按回车使用{default_folder}(会自动给你创建项目名称)：")
    if folder_path == "":
        folder_path = default_folder
    
    save_last_folder(folder_path)
    path_input = folder_path + "/" + repo_id.split('/')[-1]
    api.snapshot_download(repo_id=repo_id, local_dir=path_input, local_dir_use_symlinks=False, token=load_access_token(), repo_type=get_repo_type(current_project))

def switch_account():
    """切换账户."""
    access_token = input("请输入您的新 AccessToken: ")
    save_access_token(access_token)
    makesure_login()  # 切换账户后立即登录

def main():
    makesure_login(True)
    while True:
        print("\n请选择操作:")
        print("1. 查看项目列表")
        print("2. 切换账户")
        choice = input("请输入操作编号: ")
        if choice == "1":
            list_projects()
        elif choice == "2":
            switch_account()
        else:
            print("无效的操作编号，请重新输入")

if __name__ == "__main__":
    main()


