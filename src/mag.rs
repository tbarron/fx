use std::num::ParseFloatError;

// ----------------------------------------------------------------------------
// Computes and prints the desired output.
//
// mag_value() returns a Result containing either a String showing the
// computed result or a ParseFloatError. This result comes from
// to_float(), which mag_value() calls. print_mag() unwraps the Result
// and prints either the computed result from the String or the
// appropriate error message if that's what's in the Result.
//
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
// Returns a list of binary (divisor 1024) unit suffixes
//
fn binary_names() -> Vec<String> {
    let mut rval: Vec<String> = [].to_vec();
    for name in ["b", "Kb", "Mb", "Gb", "Tb", "Pb", "Eb", "Zb", "Yb"].iter() {
        rval.push(String::from(*name));
    }
    rval
}

// ----------------------------------------------------------------------------
// Returns a list of decimal (divisor 1000) unit suffixes
//
fn si_names() -> Vec<String> {
    let mut rval: Vec<String> = [].to_vec();
    for name in ["", "K", "M", "G", "T", "P", "E", "Z", "Y"].iter() {
        rval.push(String::from(*name));
    }
    rval
}

// ----------------------------------------------------------------------------
// Unwraps the Result and print either the computed output or the error
//
fn print_mag(result: Result<String, ParseFloatError>) {
    match result {
        Ok(n)  => println!("{}", n),
        Err(e) => println!("Error: {}", e),
    }
}

// ----------------------------------------------------------------------------
// Converts a str to a 64 bit float value. If the conversion is
// successful, returns a Result containing the the value. If the
// conversion fails, the '?' that follows the parse function returns a
// Result containing the error.
//
fn to_float(val: &str) -> Result<f64, ParseFloatError> {
    let val: String = val.replace("_", "");
    let val = val.trim().parse::<f64>()?;
    Ok(val)
}

// ----------------------------------------------------------------------------
// Given a str value, a divisor, and a list of suffixes, compute the
// floating point number of appropriate units to forat into a String
// and return.
//
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
// Tests
//
#[cfg(test)]
mod tests {
    use super::*;

    // ------------------------------------------------------------------------
    // Tests of to_float()
    //
    #[test]
    fn test_to_float() {
        assert_eq!(to_float("12.25"), Ok(12.25));
        assert_eq!(to_float("123_412.7829"), Ok(123412.7829));
        assert_eq!(to_float("  123_412.00000007"), Ok(123412.00000007));
        assert_eq!(to_float("  6_827_123_412.00002"), Ok(6827123412.00002));
    }

    // ------------------------------------------------------------------------
    // Tests of mag_value() with no underscores in the input
    //
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
    // Tests of mag_value() with underscores in the input
    //
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
    // Tests of mag_value() with underscores and divisor 1024 in the input
    //
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
