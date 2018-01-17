use std::num::ParseFloatError;

// ----------------------------------------------------------------------------
pub fn mag(values: &[&str]) {
    for value in values {
        print_mag(mag_value(value));
    }
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
fn mag_value(val: &str) -> Result<String, ParseFloatError> {
    let mut idx = 0;
    let mut val: f64 = match to_float(val) {
        Ok(num) => num,
        Err(e)  => return Err(e),
    };
    let sizes = ["b", "Kb", "Mb", "Gb", "Tb", "Pb", "Eb", "Zb", "Yb"];
    while 1000.0 < val {
        idx += 1;
        val /= 1000.0;
    };
    Ok(format!("{:.*} {}", 3, val, sizes[idx]))
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
        assert_eq!(mag_value("1241"), Ok(String::from("1.241 Kb")));
        assert_eq!(mag_value("1241995"), Ok(String::from("1.242 Mb")));
        assert_eq!(mag_value("1249900000"), Ok(String::from("1.250 Gb")));
    }

    // ------------------------------------------------------------------------
    #[test]
    fn test_mag_underscore() {
        assert_eq!(mag_value("1_241"), Ok(String::from("1.241 Kb")));
        assert_eq!(mag_value("1_241_700"), Ok(String::from("1.242 Mb")));
        assert_eq!(mag_value("1_241_000_000"), Ok(String::from("1.241 Gb")));
    }
}
