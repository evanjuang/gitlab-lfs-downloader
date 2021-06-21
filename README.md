# gitlab-lfs-downloader
Download LFS single file on Gitlab  
[Reference](http://blog.evolution515.net/2020/08/12/download-an-lfs-backed-file-from-gitlab-com-without-git-and-git-lfs-installed/)
### Install pacakges
```
pip install requests python-dotenv tqdm
```
### Create `.env` file
```
GIT_HOST=gitlab.com/example
GIT_TOKEN=<Gitlab PRIVATE-TOKEN>
GIT_USER=user
GIT_PWD=password
```
### Usage
```
gitlfs-downloader.py [-h] project ref file

project: project path, ex: my_group/my_project
ref    : branch, tag, or commit
file   : file path on repository, ex: my_dir/filename.img
```
