from fabric.api import local,lcd


def build():
    # local("jupyter nbconvert docs/**/*.ipynb --to markdown")
    local("copy README.md docs\index.md")
    local("mkdocs build")
    with lcd("..\East196.github.io"):
        local("rd /s /q aispider")
    local("xcopy site ..\East196.github.io\oxdeepnlp\ /s /e")


def serve():
    local("mkdocs serve")
