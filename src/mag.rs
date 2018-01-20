use std::num::ParseFloatError;

// ----------------------------------------------------------------------------
pub fn mag(binary: bool, values: &[&str]) {
    for value in values {
        if binary {
            print_mag(mag_value(value, 1024.0, binary_names()));
        } else {
            print_mag(mag_value(value, 1000.0, si_names()));
        }
    }
}

// ----------------------------------------------------------------------------
fn binary_names() -> Vec<String> {
    let mut rval: Vec<String> = [].to_vec();
    for name in ["b", "Kb", "Mb", "Gb", "Tb", "Pb", "Eb", "Zb", "Yb"].iter() {
        rval.push(String::from(*name));
    }
    rval
}

// ----------------------------------------------------------------------------
fn si_names() -> Vec<String> {
    let mut rval: Vec<String> = [].to_vec();
    for name in ["", "K", "M", "G", "T", "P", "E", "Z", "Y"].iter() {
        rval.push(String::from(*name));
    }
    rval
}

// ----------------------------------------------------------------------------
fn print_mag(result: Result<String, ParseFloatError>) {
    match result {
        Ok(n)  => println!("{}", n),
        Err(e) => println!("Error: {}", e),
    }
}

// ----------------------------------------------------------------------------
fn to_float(val: &str) -> Result<f64, ParseFloatError> {
    let val: String = val.replace("_", "");
    let val = val.trim().parse::<f64>()?;
    Ok(val)
}

// ----------------------------------------------------------------------------
fn mag_value(val: &str, divisor: f64, namelist: Vec<String>)
             -> Result<String, ParseFloatError> {
    let mut idx = 0;
    let mut val: f64 = match to_float(val) {
        Ok(num) => num,
        Err(e)  => return Err(e),
    };
    while divisor < val {
        idx += 1;
        val /= divisor;
    };
    Ok(format!("{:.*} {}", 3, val, namelist[idx]))
}

// ----------------------------------------------------------------------------
#[cfg(test)]
mod tests {
    use super::*;

    // ------------------------------------------------------------------------
    #[test]
    fn test_to_float() {
        assert_eq!(to_float("12.25"), Ok(12.25));
        assert_eq!(to_float("123_412.7829"), Ok(123412.7829));
        assert_eq!(to_float("  123_412.00000007"), Ok(123412.00000007));
        assert_eq!(to_float("  6_827_123_412.00002"), Ok(6827123412.00002));
    }

    // ------------------------------------------------------------------------
    #[test]
    fn test_mag_no_underscore() {
        assert_eq!(mag_value("1241", 1000.0, si_names()),
                   Ok(String::from("1.241 K")));
        assert_eq!(mag_value("1241995", 1000.0, si_names()),
                   Ok(String::from("1.242 M")));
        assert_eq!(mag_value("1249900000", 1000.0, si_names()),
                   Ok(String::from("1.250 G")));
    }

    // ------------------------------------------------------------------------
    #[test]
    fn test_mag_underscore() {
        assert_eq!(mag_value("1_241", 1000.0, si_names()),
                   Ok(String::from("1.241 K")));
        assert_eq!(mag_value("1_241_700", 1000.0, si_names()),
                   Ok(String::from("1.242 M")));
        assert_eq!(mag_value("1_241_000_000", 1000.0, si_names()),
                   Ok(String::from("1.241 G")));
    }

    // ------------------------------------------------------------------------
    #[test]
    fn test_mag_binary() {
        assert_eq!(mag_value("1_241", 1024.0, binary_names()),
                   Ok(String::from("1.212 Kb")));
        assert_eq!(mag_value("1_241_700", 1024.0, binary_names()),
                   Ok(String::from("1.184 Mb")));
        assert_eq!(mag_value("1_241_000_000", 1024.0, binary_names()),
                   Ok(String::from("1.156 Gb")));
    }
}
