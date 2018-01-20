//use std::process::Command;
use super::*;

// ----------------------------------------------------------------------------
pub fn cmd(dryrun: bool, verbose: bool, command: &str, items: &[&str]) {
    for filled in _cmdlist(command, items) {
        if dryrun {
            would_do(&filled);
        } else {
            if verbose {
                println!("> {}", &filled);
            }
            run(&filled);
        }
    }
}

// ----------------------------------------------------------------------------
fn _cmdlist(command: &str, items: &[&str]) -> Vec<String> {
    let mut rvec: Vec<String> = Vec::new();
    for item in items {
        let full = String::from(command.replace('%', item));
        rvec.push(full);
    }
    rvec
}

// ----------------------------------------------------------------------------
#[cfg(test)]
mod tests {
    use super::*;

    // ------------------------------------------------------------------------
    #[test]
    fn test_cmd_make_list() {
        assert_eq!(_cmdlist("echo %", &["foo", "bar", "xyzzy"]),
                   ["echo foo", "echo bar", "echo xyzzy"]);
    }
}
