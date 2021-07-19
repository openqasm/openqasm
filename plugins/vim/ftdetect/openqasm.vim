" Register syntax for .qasm files as OpenQASM

function s:parse_version_header()
    " Parse the 'OPENQASM <version>;' header in the file (if present), and store
    " the value in 'b:openqasm_version' for consumption by the syntax file.
    "
    " This is a pretty naive way of parsing the version header information.  It
    " doesn't parse comments, and doesn't handle cases where the header is
    " split onto multiple lines.
    if exists("g:openqasm_version_override")
        return
    let [linenum, colnum] = searchpos('\vOPENQASM\s+[0-9]+(\.[0-9]+)?', 'n')
    if linenum == 0
        return 
    endif
    let line = getline(linenum)
    let match = matchstr(line, '\v[0-9]+(\.[0-9]+)?')
    " The version string in the OpenQASM grammar is actually defined as a
    " float (rather than something that's aware of semantic versioning), so we
    " don't have to do anything clever.
    let b:openqasm_version = str2float(match)
endfunction

au BufNewFile,BufRead *.qasm    call s:parse_version_header()
au BufNewFile,BufRead *.qasm    setl filetype=openqasm
