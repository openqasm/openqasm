function openqasm#get_version()
    " Return a float of the version to use when handling this OpenQASM file.
    " This will be the version override if set, otherwise the value specified
    " in the 'OPENQASM <version>' header, or the fallback.
    "
    " This is a pretty naive way of parsing the version header information.  It
    " doesn't parse comments, and doesn't handle cases where the header is
    " split onto multiple lines.
    if exists("g:openqasm_version_override")
        return str2float(g:openqasm_version_override)
    endif
    let [linenum, colnum] = searchpos('\vOPENQASM\s+[0-9]+(\.[0-9]+)?', 'n')
    if linenum == 0
        return get(g:, 'openqasm_version_fallback', 3.0)
    endif
    let line = getline(linenum)
    let match = matchstr(line, '\v[0-9]+(\.[0-9]+)?')
    " The version string in the OpenQASM grammar is actually defined as a
    " float (rather than something that's aware of semantic versioning), so we
    " don't have to do anything clever.
    return str2float(match)
endfunction
