use std::process::Command;

// ----------------------------------------------------------------------------
pub fn range(dryrun: bool, rcmd: &str, lohigh: &str) {
    // split up the low:high range string
    let tup: (i32, i32) = get_low_high(&lohigh);
    let cmds = _rnglist(rcmd, tup.0, tup.1);
    for cmd in cmds {
        if dryrun {
            println!("would do '{}'", cmd);
        } else {
            run(&cmd);
        }
    }
}

// ----------------------------------------------------------------------------
fn _rnglist(cmd: &str, low: i32, high: i32) -> Vec<String> {
    let mut rvec: Vec<String> = Vec::new();
    for num in low .. high {
        let num_s = format!("{}", num);
        let full = String::from(cmd.replace('%', num_s.as_str()));
        rvec.push(full)
    }
    rvec
}

// ----------------------------------------------------------------------------
fn get_low_high(lowhigh: &str) -> (i32, i32) {
    let mut rvec: Vec<String> = Vec::new();
    if lowhigh.contains(":") {
        for item in lowhigh.split(":") {
            rvec.push(String::from(item))
        }
    } else if lowhigh.contains("..") {
        for item in lowhigh.split("..") {
            rvec.push(String::from(item))
        }
    }
    let low: i32 = rvec[0].parse::<i32>().unwrap();
    let high: i32 = rvec[1].parse::<i32>().unwrap();

    (low, high)
}

// ----------------------------------------------------------------------------
fn run(cmd: &String) {
    let mut cvec: Vec<String> = Vec::new();
    for item in cmd.split(" ") {
        cvec.push(String::from(item));
    }
    if let Ok(mut child) = Command::new(&cvec[0])
        .args(&cvec[1..])
        .spawn() {
        child.wait()
            .expect(format!("failure running '{}'", cmd).as_str());
    } else {
        println!("'{}' never started", cmd);
    }
}

// ----------------------------------------------------------------------------
#[cfg(test)]
mod tests {
    use super::*;

    // ------------------------------------------------------------------------
    #[test]
    fn test_rng_glh_colon() {
        let tup: (i32, i32) = get_low_high("5:9");
        assert_eq!(tup.0, 5);
        assert_eq!(tup.1, 9);
    }

    // ------------------------------------------------------------------------
    #[test]
    fn test_rng_glh_dotdot() {
        let tup: (i32, i32) = get_low_high("18..27");
        assert_eq!(tup.0, 18);
        assert_eq!(tup.1, 27);
    }

    // ------------------------------------------------------------------------
    #[test]
    fn test_rng_make_list() {
        assert_eq!(_rnglist("echo %", 7, 13),
                   ["echo 7", "echo 8", "echo 9", "echo 10", "echo 11",
                    "echo 12", ]);
    }
}
