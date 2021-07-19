# openqasm.vim

A Vim plugin for syntax highlighting of OpenQASM files.

<img alt="Example syntax highlighting of an OpenQASM file with the solarized-dark color scheme" src="https://user-images.githubusercontent.com/5968590/126172538-2863ad68-89da-4d43-b7f4-a9895586b70a.png" width=343px /> <img alt="Example syntax highlighting of an OpenQASM file with the solarized-light color scheme" src="https://user-images.githubusercontent.com/5968590/126172543-ce9b23e3-5ba0-4ced-b233-25f4bc7c90c7.png" width=343px />


## Installation

### [Vundle](https://github.com/VundleVim/Vundle.vim)

Add the line
```vim
Plugin 'Qiskit/openqasm', {'rtp': 'plugins/vim/'}
```
into your `.vimrc` between the `call vundle#begin()` and `call vundle#end()` lines, reload, and run `:PluginInstall`.

### [vim-plug](https://github.com/junegunn/vim-plug)

Add the line
```vim
Plug 'Qiskit/openqasm', {'rtp': 'plugins/vim/'}
```
into your `.vimrc` between the `call plug#begin()` and `call plug#end()` lines, reload, and run `:PlugInstall`.

### Bare Vim

Clone this repository somewhere locally with

```bash
$ cd <plugins path>
$ git clone https://github.com/Qiskit/openqasm
```

This does not need to be in the `.vim` directory.
Now add the plugin's subdirectory to Vim's runtime path, by adding the following to your `.vimrc`:

```vim
set rtp+='<plugins path>/openqasm/plugins/vim'
```

Reload `.vimrc` to load the plugin.



## Usage

At present, this only provides syntax highlighting file for OpenQASM files, which automatically registers itself for all files with the name `*.qasm`.
To turn on syntax highlighting for another file (for example `stdgates.inc`), call
```vim
:set filetype=openqasm
```
either as a command, or as part of an autocommand.

The default highlighting groups are defined at the bottom of the file `syntax/openqasm.vim`.
You can override these in your own configuration files (`.vimrc`, etc) if you prefer different groupings.

The plugin attempts to determine the OpenQASM version from the required `OPENQASM <version>;` statement at the top of the file, and falls back to OpenQASM 3.0 if this is unparseable (perhaps on multiple lines) or not present.
You can control the fallback value by setting
```vim
let g:openqasm_version_fallback = 2.0
```
in your `.vimrc` file.
You can override all version checking with
```vim
let g:openqasm_version_override = 2.0
```

For full help, call
```vim
    :help openqasm
```


## Limitations

No attempt is made to highlight the arbitrary grammars present inside `defcal` blocks of OpenQASM 3.
This would be strongly dependent on the grammar file loaded by the `defcalgrammar` statement.


## License

openqasm.vim is licensed under the Apache 2.0 open-source license, along with the rest of the OpenQASM source.
See the `LICENSE` file in the root of this repository for more information.
