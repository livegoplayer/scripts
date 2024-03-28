import os

def test():
    os.environ["HTTP_PROXY"] = ""
    os.environ["HTTPS_PROXY"] = ""
    mirror_url = "https://hf-mirror.com"
    os.environ['HF_ENDPOINT'] = mirror_url

    from huggingface_hub import HfApi

    token = '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' #my token
    api = HfApi(endpoint=mirror_url, token=token) 
    repo_id = 'xjyplayer/test_file'
    api.upload_file(repo_id=repo_id, path_or_fileobj='F:\p站下载\泛光.safetensors', path_in_repo="test/8x_NMKD-Superscale_150000_G.pth", commit_message="11", token=token)

if __name__ == "__main__":
    test()