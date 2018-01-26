use super::*;

// ----------------------------------------------------------------------------
// This function reads tokens from stdin and inserts them into
// *command* where the replstr ('%' by default) is, limiting the total
// length of command lines to 256 bytes or less. With *dryrun*, just
// report the generated commands without actually running them. With
// *verbose*, report the generated commands before running each one.
//
pub fn xargs(dryrun: bool, verbose: bool, replstr: &str, command: &str) {
    let mut lrepl = replstr;
    if lrepl == "" {
        lrepl = "%";
    }
    if command.contains(lrepl) {
        let cl: Vec<String> = _cmdlist(command, lrepl);
        for cmd in cl {
            if dryrun {
                would_do(&cmd);
            } else {
                if verbose {
                    println!("> '{}'", cmd);
                }
                run(&cmd);
            }
        }
    } else {
        println!("No '{}' found in '{}'", lrepl, command);
    }
}

// ----------------------------------------------------------------------------
// Constructs and returns a list of commands from *command* and stdin,
// putting strings of tokens into *command* in place of the replstr
// ('%' by default)
//
fn _cmdlist(command: &str, replstr: &str) -> Vec<String> {
    let stdin = read_file("<stdin>");
    let mut rval: Vec<String> = Vec::new();
    let mut collect = String::new();
    for item in stdin.split_whitespace() {
        if item.len() + 1 + collect.len() + command.len() < 256 {
            if 0 < collect.len() { collect.push_str(" "); }
            collect.push_str(item);
        } else {
            let cmd: String = command.replace(replstr, collect.as_str());
            rval.push(cmd);
            collect = String::from(item);
        }
    }

    if 0 < collect.len() {
        let cmd: String = command.replace(replstr, collect.as_str());
        rval.push(cmd);
    }

    rval
}
