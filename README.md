# gitlab-lfs-downloader
Download LFS single file on Gitlab  
[Reference](http://blog.evolution515.net/2020/08/12/download-an-lfs-backed-file-from-gitlab-com-without-git-and-git-lfs-installed/)


### Create `.env` file
```
GIT_HOST=gitlab.com/example
GIT_TOKEN=<Gitlab PRIVATE-TOKEN>
GIT_USER=user
GIT_PWD=password
```
### Usage
```
gitlfs-downloader.py [-h] project ref file [-o OUTPUT_DIR]

project: project path (ex: my_group/my_project)
ref    : branch, tag, or commit
file   : file path on repository (ex: my_dir/filename.img)

-o, --output-dir <OUTPUT_DIR>: Download to the OUTPUT_DIR, default is the current working directory.
```
