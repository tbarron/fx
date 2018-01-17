// ----------------------------------------------------------------------------
pub fn odx(values: &[&str]) {
    // let mut first = true;
    for arg in values {
        if is_hex(arg) {
            println!( "{}", refract(arg, 16) );
        } else if is_octal(arg) {
            println!( "{}", refract(arg, 8) );
        } else if is_binary(arg) {
            println!( "{}", refract(arg, 2) );
        } else if is_decimal(arg) {
            println!( "{}", refract(arg, 10) );
        } else {
            println!("'{}' is not a valid hex, octal, \
                      binary, or decimal value",
                    arg);
        }
    }
}

// ----------------------------------------------------------------------------
// Given a string and a radix (2, 8, 10, or 16), convert the string
fn refract(arg: &str, radix: u32) -> String {
    let value: &str = arg.trim();
    let value: i64 =
        if radix != 10 {
            i64::from_str_radix(&value[2..], radix).expect("bad value")
        } else {
            i64::from_str_radix(value, radix).expect("bad value")
        };
    format!("0x{:x} == {} == 0o{:o} == 0b{:b}",
             value, value, value, value)
}

// ----------------------------------------------------------------------------
fn is_hex(arg: &str) -> bool {
    let chrs: Vec<char> = arg.trim().chars().collect();
    chrs[0] == '0' && chrs[1] == 'x'
}

// ----------------------------------------------------------------------------
fn is_octal(arg: &str) -> bool {
    let chrs: Vec<char> = arg.trim().chars().collect();
    chrs[0] == '0' && chrs[1] == 'o'
}

// ----------------------------------------------------------------------------
fn is_binary(arg: &str) -> bool {
    let chrs: Vec<char> = arg.trim().chars().collect();
    chrs[0] == '0' && chrs[1] == 'b'
}

// ----------------------------------------------------------------------------
fn is_decimal(arg: &str) -> bool {
    let result;
    let _value: i32 = match arg.trim().parse() {
        Ok(num)  => { result = true; num }
        Err(_)   => { result = false; 0 }
    };
    result
}

// ----------------------------------------------------------------------------
#[cfg(test)]
mod tests {
    use super::*;

    // ------------------------------------------------------------------------
    #[test]
    fn test_refract() {
        assert_eq!(refract("0b110110", 2),
                   "0x36 == 54 == 0o66 == 0b110110");
        assert_eq!(refract("   0b110110", 2),
                   "0x36 == 54 == 0o66 == 0b110110");
        assert_eq!(refract("0o110110", 8),
                   "0x9048 == 36936 == 0o110110 == 0b1001000001001000");
        assert_eq!(refract("   0o110110", 8),
                   "0x9048 == 36936 == 0o110110 == 0b1001000001001000");
        assert_eq!(refract("110110", 10),
                   "0x1ae1e == 110110 == 0o327036 == 0b11010111000011110");
        assert_eq!(refract("   110110", 10),
                   "0x1ae1e == 110110 == 0o327036 == 0b11010111000011110");
        assert_eq!(refract("0x110110", 16),
                   "0x110110 == 1114384 == 0o4200420 == \
                   0b100010000000100010000");
        assert_eq!(refract("   0x110110", 16),
                   "0x110110 == 1114384 == 0o4200420 == \
                   0b100010000000100010000");
    }

    // ------------------------------------------------------------------------
    #[test]
    fn test_is_hex() {
        assert!(   is_hex("0x100"));
        assert!(   is_hex("   0x100"));
        assert!(   is_hex("0x100   "));
        assert!( ! is_hex("12345"));
        assert!( ! is_hex("0o12345"));
        assert!( ! is_hex("0b10101010"));
        assert!( ! is_hex("one two three"));
    }

    // ------------------------------------------------------------------------
    #[test]
    fn test_is_octal() {
        assert!( ! is_octal("0x100"));
        assert!( ! is_octal("12345"));
        assert!(   is_octal("0o12345"));
        assert!(   is_octal("0o12345    "));
        assert!(   is_octal("    0o12345"));
        assert!( ! is_octal("0b10101010"));
        assert!( ! is_octal("one two three"));
    }

    // ------------------------------------------------------------------------
    #[test]
    fn test_is_binary() {
        assert!( ! is_binary("0x100"));
        assert!( ! is_binary("12345"));
        assert!( ! is_binary("0o12345"));
        assert!(   is_binary("0b10101010"));
        assert!(   is_binary("   0b10101010"));
        assert!(   is_binary("0b10101010   "));
        assert!( ! is_binary("one two three"));
    }

    // ------------------------------------------------------------------------
    #[test]
    fn test_is_decimal() {
        assert!( ! is_decimal("0x100"));
        assert!(   is_decimal("12345"));
        assert!(   is_decimal("   12345"));
        assert!(   is_decimal("12345   "));
        assert!( ! is_decimal("0o12345"));
        assert!( ! is_decimal("0b10101010"));
        assert!( ! is_decimal("one two three"));
    }
}