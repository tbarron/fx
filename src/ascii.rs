// NAMES:
//     ["NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL", "BS",
//     "TAB", "LF", "VT", "FF", "CR", "SO", "SI", "DLE", "DC1", "DC2",
//     "DC3", "DC4", "NAK", "SYN", "ETB", "CAN", "EM", "SUB", "ESC",
//     "FS", "GS", "RS", "US", "SPC"];



// ----------------------------------------------------------------------------
// Display the ascii code table
pub fn ascii() {
    // let mut line = String::from("");
    // let names = ["NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL",
    //              "BS",  "TAB", "LF",  "VT",  "FF",  "CR",  "SO",  "SI",
    //              "DLE", "DC1", "DC2", "DC3", "DC4", "NAK", "SYN", "ETB",
    //              "CAN", "EM",  "SUB", "ESC", "FS",  "GS",  "RS",  "US",
    //              "SPC"];
    // let mut ldx = 0;
    // let mut ord: usize;
    // while ldx < 0x80 {
    //     for off in 0..8 {
    //         ord = ldx + off;
    //         if ord <= 0x20 {
    //             let prt = names[ord];
    //             line = format!("{0}0x{1:02x} {chr:<wid$} ",
    //                            line, ord, chr=prt, wid=3);
    //         } else if ord < 0x7f {
    //             let charval: u8 = ord as u8;
    //             let prt = charval as char;
    //             line = format!("{0}0x{1:02x} {chr:<wid$} ",
    //                            line, ord, chr=prt, wid=3);
    //         }
    //     }
    //     println!("{}", line);
    //     line = String::from("");
    //     ldx += 8;
    // }
    println!("{}", ascii_text());
}

// ----------------------------------------------------------------------------
// Construct the ascii code table for display in a string
fn ascii_text() -> String {
    let mut line = String::from("");
    let mut rval = String::from("");
    let mut sep = String::from("");
    let names = ["NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL",
                 "BS",  "TAB", "LF",  "VT",  "FF",  "CR",  "SO",  "SI",
                 "DLE", "DC1", "DC2", "DC3", "DC4", "NAK", "SYN", "ETB",
                 "CAN", "EM",  "SUB", "ESC", "FS",  "GS",  "RS",  "US",
                 "SPC"];
    let mut ldx = 0;
    let mut ord: usize;
    while ldx < 0x80 {
        for off in 0..8 {
            ord = ldx + off;
            if ord <= 0x20 {
                let prt = names[ord];
                line = format!("{0}0x{1:02x} {chr:<wid$} ",
                               line, ord, chr=prt, wid=3);
            } else if ord < 0x7f {
                let charval: u8 = ord as u8;
                let prt = charval as char;
                line = format!("{0}0x{1:02x} {chr:<wid$} ",
                               line, ord, chr=prt, wid=3);
            }
        }
        rval = format!("{}{}{}", rval, sep, line);
        sep = String::from("\n");
        line = String::from("");
        ldx += 8;
    }
    return rval
}

// ----------------------------------------------------------------------------
// fn ascii_names() -> [str; 4] {
//     ["NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL",
//      "BS",  "TAB", "LF",  "VT",  "FF",  "CR",  "SO",  "SI",
//      "DLE", "DC1", "DC2", "DC3", "DC4", "NAK", "SYN", "ETB",
//      "CAN", "EM",  "SUB", "ESC", "FS",  "GS",  "RS",  "US",
//      "SPC"]
// }

// ----------------------------------------------------------------------------
#[cfg(test)]
mod tests {
    use super::*;

    // ------------------------------------------------------------------------
    #[test]
    fn test_ascii() {
        assert!(ascii_text().contains(" SOH "));
    }

    // ------------------------------------------------------------------------
    // Verify that all the hex values show up in the output
    #[test]
    fn test_ascii_count() {
        let text = ascii_text();
        for val in 0..0x7f {
            let needle = format!("0x{:02x} ", val);
            assert!(text.contains(&needle));
        }
    }

    // ------------------------------------------------------------------------
    // Verify that all the character names appear in the output.
    // Ideally, I'd like to write a function called something like
    // ascii_names() that returns the array used below (and also in
    // ascii_text(). But I haven't figured out how to get rust to let
    // me do that yet. :(
    #[test]
    fn test_ascii_low() {
        let names = ["NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL",
                     "BS",  "TAB", "LF",  "VT",  "FF",  "CR",  "SO",  "SI",
                     "DLE", "DC1", "DC2", "DC3", "DC4", "NAK", "SYN", "ETB",
                     "CAN", "EM",  "SUB", "ESC", "FS",  "GS",  "RS",  "US",
                     "SPC"];
        let text = ascii_text();

        for name in names.iter() {
            assert!(text.contains(name));
        }
    }

    // ------------------------------------------------------------------------
    // #[test]
    // fn test_ascii_names() {
    //     let text = ascii_text();
    //     for item in ascii_names() {
    //         let spitem = String::from(" " + item);
    //         assert!(text.contains(spitem))
    //     }
    // }
}
