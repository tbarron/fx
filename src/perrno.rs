use std::collections::HashMap;
use regex::Regex;
use super::*;

// ----------------------------------------------------------------------------
// Given an integer value in range or a valid error name, print
// information about that error. If a number is out of range or a name
// is not recognized, the failing keys are reported.
//
pub fn perrno(values: &[&str]) {
    let by_num = err_list();
    let by_name = index_by_name(&by_num);
    let bad_value = (-1, String::from(""), String::from(""));
    for item in values {
        let num = str_to_int32(item, -1);
        if 0 < num {
            let tup = match by_num.get(&num) {
                Some(tup) => &tup,
                None      => &bad_value
            };
            if 0 < tup.0 {
                println!("{} ({}): {}", tup.1, tup.0, tup.2);
            } else {
                println!("No error entry found for {}", num);
            }
            continue;
        }

        let s_item = String::from(*item);
        let tup = match by_name.get(&s_item) {
            Some(tup) => &tup,
            None      => &bad_value
        };
        if 0 < tup.0 {
            println!("{} ({}): {}", tup.1, tup.0, tup.2);
        } else {
            println!("No error entry found for {}", item);
        }
    }
}

// ----------------------------------------------------------------------------
// Given a hash map indexed by error number (i32), create a copy
// indexed by name (String).
//
fn index_by_name(by_num: &HashMap<i32, (i32, String, String)>)
                 -> HashMap<String, (i32, String, String)> {
    let mut var = HashMap::new();
    for item in by_num {
        let tup = item.1.clone();
        let key = tup.1.clone();
        var.insert(key, tup);
    }
    var
}

// ----------------------------------------------------------------------------
// Read /usr/include/sys/errno.h and build the by_name HashMap from it
//
fn err_list() -> HashMap<i32, (i32, String, String)> {
    let mut rval = HashMap::new();
    let data = read_file("/usr/include/sys/errno.h");
    let rgxstr = r"#define\s(E\w*)\s+(\d+)\s+/\*\s+(\S[^*]*)\s\*/";
    let rgx = Regex::new(rgxstr).unwrap();

    for item in rgx.captures_iter(data.as_str()) {
        let value = str_to_int32(&item[2], -1);
        if value < 0 {
            continue;
        }
        let name = String::from(&item[1]);
        let desc = String::from(&item[3]);
        if ! rval.contains_key(&value) {
            rval.insert(value, (value, name, desc));
        }
    }
    rval
}
