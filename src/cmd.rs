use super::*;

// ----------------------------------------------------------------------------
// Handle a command with options dryrun, verbose, and items that will
// be subbed into the command where '%' appears.
//
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
// Generate a list of commands, one for each item with the item subbed
// into the command
//
fn _cmdlist(command: &str, items: &[&str]) -> Vec<String> {
    let mut rvec: Vec<String> = Vec::new();
    for item in items {
        let full = String::from(command.replace('%', item));
        rvec.push(full);
    }
    rvec
}

// ----------------------------------------------------------------------------
// tests
//
#[cfg(test)]
mod tests {
    use super::*;

    // ------------------------------------------------------------------------
    // Verify that _cmdlist() generates the expected list of commands
    // given a basic command and a list of items
    //
    #[test]
    fn test_cmd_make_list() {
        assert_eq!(_cmdlist("echo %", &["foo", "bar", "xyzzy"]),
                   ["echo foo", "echo bar", "echo xyzzy"]);
    }
}
