pub fn mag(values: &[&str]) {
    println!("This is the mag module: {:?}", values)
// ----------------------------------------------------------------------------
#[cfg(test)]
mod tests {
    use super::*;

    // ------------------------------------------------------------------------
    #[test]
    fn test_to_float() {
        assert_eq!(to_float("12.25"), 12.25);
        assert_eq!(to_float("123_412.7829"), 123412.7829);
        assert_eq!(to_float("  123_412.00000007"), 123412.00000007);
        assert_eq!(to_float("  6_827_123_412.00002"), 6827123412.00002);
    }

    // ------------------------------------------------------------------------
    #[test]
    fn test_mag_no_underscore() {
        assert_eq!(mag_value("1241"), "1.241 Kb");
        assert_eq!(mag_value("1241995"), "1.242 Mb");
        assert_eq!(mag_value("1249900000"), "1.250 Gb");
    }

    // ------------------------------------------------------------------------
    #[test]
    fn test_mag_underscore() {
        assert_eq!(mag_value("1_241"), "1.241 Kb");
        assert_eq!(mag_value("1_241_700"), "1.242 Mb");
        assert_eq!(mag_value("1_241_000_000"), "1.241 Gb");
    }
}
