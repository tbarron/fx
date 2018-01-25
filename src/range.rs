use std::process;
use super::*;

// ----------------------------------------------------------------------------
// Generate a list of commands for a set of numbers
//
pub fn range(dryrun: bool, verbose: bool, rcmd: &str, lohigh: &str,
             zpad: usize) {
    // split up the low:high range string
    let tup: (i32, i32) = get_low_high(&lohigh);
    let cmds = _rnglist(rcmd, zpad, tup.0, tup.1);
    for cmd in cmds {
        if dryrun {
            would_do(&cmd);
        } else {
            if verbose {
                println!("> {}", &cmd);
            }
            run(&cmd);
        }
    }
}

// ----------------------------------------------------------------------------
// For each value between *low* and *high*, generates *cmd* with the
// number subbed in for '%'. If _zpad is not 0, enough '0' characters
// are prepended to make the number that wide.
//
fn _rnglist(cmd: &str, _zpad: usize, low: i32, high: i32) -> Vec<String> {
    let mut rvec: Vec<String> = Vec::new();
    for num in low .. high {
        let num_s = format!("{:0zpad$}", num, zpad=_zpad);
        let full = String::from(cmd.replace('%', num_s.as_str()));
        rvec.push(full)
    }
    rvec
}

// ----------------------------------------------------------------------------
// Parses the *lowhigh* value to establish the desired range.
//
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

    let low: i32 = str_to_int32(rvec[0].as_str(), -1);
    let high: i32 = str_to_int32(rvec[1].as_str(), -1);
    if low < 0 || high < 0 {
        println!("Attempt to parse '{}' failed", lowhigh);
        process::exit(1);
    };

    (low, high)
}

// ----------------------------------------------------------------------------
// Tests
//
#[cfg(test)]
mod tests {
    use super::*;

    // ------------------------------------------------------------------------
    // Test range parser with a ':' as a separator
    //
    #[test]
    fn test_rng_glh_colon() {
        let tup: (i32, i32) = get_low_high("5:9");
        assert_eq!(tup.0, 5);
        assert_eq!(tup.1, 9);
    }

    // ------------------------------------------------------------------------
    // Test range parser with a '..' as a separator
    //
    #[test]
    fn test_rng_glh_dotdot() {
        let tup: (i32, i32) = get_low_high("18..27");
        assert_eq!(tup.0, 18);
        assert_eq!(tup.1, 27);
    }

    // ------------------------------------------------------------------------
    // Test the command list generator
    //
    #[test]
    fn test_rng_make_list() {
        assert_eq!(_rnglist("echo %", 0, 7, 13),
                   ["echo 7", "echo 8", "echo 9", "echo 10", "echo 11",
                    "echo 12", ]);
    }

    // ------------------------------------------------------------------------
    // Test the command list generator with a non-zero zpad value
    //
    #[test]
    fn test_rng_make_list_zpad() {
        assert_eq!(_rnglist("echo %", 2, 7, 13),
                   ["echo 07", "echo 08", "echo 09", "echo 10", "echo 11",
                    "echo 12", ]);
    }
}
