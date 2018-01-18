use std::process::Command;

// ----------------------------------------------------------------------------
pub fn cmd(command: &str, items: &[&str]) {
    for filled in _cmdlist(command, items) {
        let mut cvec: Vec<String> = Vec::new();
        for item in filled.split(" ") {
            cvec.push(String::from(item));
        }
        let _output = Command::new(&cvec[0])
            .args(&cvec[1..])
            .spawn()
            .expect(format!("failure running '{}'", filled).as_str());
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
