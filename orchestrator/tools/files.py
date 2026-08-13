
import os
from typing import Callable, Optional, Protocol

from llama_client import Tool
from llama_client.types.json import JSON



__all__ = (
    "list_dir",
    "read_file",
    "create_file",
    "write_file",
    "append_file",
    "replace_file",
    "file_tools"
)



class IOFuncType(Protocol):
    def __call__(self, **kwargs: JSON) -> JSON: ...


# Helper functions
def _is_path_safe(path: str, base: str = ".") -> bool:
    base_real = os.path.realpath(base)
    path_real = os.path.realpath(path)

    return base_real == path_real or path_real.startswith(base_real + os.sep)


def io_function(*path_kwargs: str) -> Callable[[Callable], IOFuncType]:
    """
    Decorator for functions that use io that ensures they can't access files outside the current directory.

    The names of all function arguments that represent a path should be passed in.
    """

    def decorator(func: Callable) -> IOFuncType:
        def wrapper(**kwargs: JSON) -> JSON:
            try:
                invalid_paths = []

                for kwarg in path_kwargs:
                    if kwarg in kwargs:
                        path: str = kwargs[kwarg] # type: ignore

                        # check if the path is in this directory or a sub directory
                        if not _is_path_safe(path):
                            invalid_paths.append(path)

                if invalid_paths:
                    return f"Can't access files or directories outside the local directory: {", ".join(map(lambda path: f"'{path}'", invalid_paths))}"

                return func(**kwargs)

            except UnicodeDecodeError:
                return f"Error decoding file!"

            except FileNotFoundError as e:
                return f"No such file or directory: '{e.filename}'"

            except FileExistsError as e:
                return f"File already exists: '{e.filename}'"

            except IsADirectoryError as e:
                return f"Path is a directory: '{e.filename}'"

            except NotADirectoryError as e:
                return f"Path is not a directory: '{e.filename}'"

            except PermissionError as e:
                if os.path.isdir(e.filename):
                    return f"Path is a directory, which can't be read: '{e.filename}'"

                return f"Permission denied: '{e.filename}'"

        return wrapper
    return decorator


# Tool functions
@io_function("dir_path")
def _list_dir(*, dir_path: str = ".") -> dict[str, list[str]]:
    paths = os.listdir(dir_path)

    return {
        "files": [
            path for path in paths if os.path.isfile(f"{dir_path}/{path}")
        ],
        "directories": [
            path for path in paths if os.path.isdir(f"{dir_path}/{path}")
        ]
    }


@io_function("file_path")
def _read_file(*, file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


@io_function("file_path")
def _create_file(*, file_path: str, contents: Optional[str] = None) -> str:
    with open(file_path, "x", encoding="utf-8") as f:
        f.write(contents or "")

    return f"File created successfully: '{file_path}'"


@io_function("file_path")
def _write_file(*, file_path: str, contents: str) -> str:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(contents)

    return f"File written to successfully: '{file_path}'"


@io_function("file_path")
def _append_file(*, file_path: str, text: str) -> str:
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(text)

    return f"File appended to successfully: '{file_path}'"


@io_function("file_path")
def _replace_file(*, file_path: str, old_string: str, new_string: str, replace_all: Optional[bool] = None) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        old_contents = f.read()

    new_contents = old_contents.replace(old_string, new_string, -1 if replace_all else 1)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_contents)

    return f"String replaced successfully: '{file_path}'"


# Tool definiitons
list_dir = Tool(**{
    "definition": {
        "function": {
            "name": "list_dir",
            "description": "Lists all of the files and directories in the given directory. Includes hidden files.",
            "parameters": {
                "properties": {
                    "dir_path": {
                        "type": "string",
                        "description": "The directory to read. Defaults to the current directory \"./\" when unspecified."
                    }
                }
            }
        }
    },
    "function": _list_dir
})

read_file = Tool(**{
    "definition": {
        "function": {
            "name": "read_file",
            "description": "Reads the contents of a file.",
            "parameters": {
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path of the file to read. Should include the file extension (such as .txt, .py, or .png)."
                    }
                },
                "required": [
                    "file_path"
                ]
            }
        }
    },
    "function": _read_file
})

create_file = Tool(**{
    "definition": {
        "function": {
            "name": "create_file",
            "description": "Creates a file with the given path. Optionally writes contents into the created file.",
            "parameters": {
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path of the file to create. Should include the file extension (such as .txt, .py, or .png)."
                    },
                    "contents": {
                        "type": "string",
                        "description": "The contents to write into the file."
                    }
                },
                "required": [
                    "file_path"
                ]
            }
        }
    },
    "function": _create_file
})

write_file = Tool(**{
    "definition": {
        "function": {
            "name": "write_file",
            "description": "Writes text to a file, replacing any contents.",
            "parameters": {
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path of the file to write to. Should include the file extension (such as .txt, .py, or .png)."
                    },
                    "contents": {
                        "type": "string",
                        "description": "The contents to write to the file."
                    }
                },
                "required": [
                    "file_path",
                    "contents"
                ]
            }
        }
    },
    "function": _write_file
})

append_file = Tool(**{
    "definition": {
        "function": {
            "name": "append_file",
            "description": "Appends text to the end of a file.",
            "parameters": {
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path of the file to append to. Should include the file extension (such as .txt, .py, or .png)."
                    },
                    "text": {
                        "type": "string",
                        "description": "The text to append to the end of the file."
                    }
                },
                "required": [
                    "file_path",
                    "append"
                ]
            }
        }
    },
    "function": _append_file
})

replace_file = Tool(**{
    "definition": {
        "function": {
            "name": "replace_file",
            "description": "Finds and replaces the given string with a new string in the specified file.",
            "parameters": {
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path of the file to replace in. Should include the file extension (such as .txt, .py, or .png)."
                    },
                    "old_string": {
                        "type": "string",
                        "description": "The string to be replaced."
                    },
                    "new_string": {
                        "type": "string",
                        "description": "The string to be replace `old_string` with."
                    },
                    "replace_all": {
                        "type": "boolean",
                        "description": "Whether to replace all instances of `old_string` with `new_string`. Defaults to false, only replacing the first instance."
                    }
                },
                "required": [
                    "file_path",
                    "old_string",
                    "new_string"
                ]
            }
        }
    },
    "function": _replace_file
})


# Collection of all file tools
file_tools = (
    list_dir,
    read_file,
    create_file,
    write_file,
    append_file,
    replace_file
)
