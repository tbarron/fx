extern crate clap;
use clap::{App, SubCommand, Arg};

fn main() {
    let matches = App::new("fx")
        .version("0.0.1")
        .author("Tom Barron <tusculum@gmail.com>")
        .about("Command line effects (fx, get it?)")
        .subcommand(SubCommand::with_name("ascii")
                    .about("show the ascii code table")
                   )
        .subcommand(SubCommand::with_name("odx")
                    .about("report hex, octal, binary values")
                    .arg(Arg::with_name("number")
                         .help("value to convert")
                         .required(true)
                         .min_values(1)
                        )
                   )
        .subcommand(SubCommand::with_name("cmd")
                    .about("replace % with arguments")
                    .arg(Arg::with_name("dryrun")
                         .short("n")
                         .long("dryrun")
                         .help("report what would happen without acting")
                        )
                    .arg(Arg::with_name("command")
                         .help("string with '%'")
                         .required(true)
                        )
                    .arg(Arg::with_name("items")
                         .help("% replacements")
                         .required(true)
                         .min_values(1)
                        )
                   )
        .subcommand(SubCommand::with_name("rename")
                    .about("rename files based on a s/foo/bar/ expr")
                    .arg(Arg::with_name("dryrun")
                         .short("n")
                         .long("dryrun")
                         .help("report what would happen without acting")
                         )
                    .arg(Arg::with_name("substitute")
                         .help("s/old/new/")
                         .required(true)
                        )
                    .arg(Arg::with_name("items")
                         .help("% replacements")
                         .required(true)
                         .min_values(1)
                        )
                   )
        .subcommand(SubCommand::with_name("range")
                    .about("replace % in command with nums from range")
                    .arg(Arg::with_name("dryrun")
                         .short("n")
                         .long("dryrun")
                         .help("report what would happen without acting")
                        )
                    .arg(Arg::with_name("command")
                         .help("string with '%'")
                         .required(true)
                        )
                    .arg(Arg::with_name("lohigh")
                         .short("i")
                         .help("low:high range from low to high-1")
                         .required(true)
                        )
                   )
        .subcommand(SubCommand::with_name("xargs")
                    .about("replace % in command with clumps of args")
                    .arg(Arg::with_name("dryrun")
                         .short("n")
                         .long("dryrun")
                         .help("report what would happen without acting")
                        )
                    .arg(Arg::with_name("command")
                         .help("string with '%'")
                         .required(true)
                        )
                   )
        .get_matches();

    if matches.is_present("ascii") {
        ascii();
    } else if matches.is_present("odx") {
        if let Some(matches) = matches.subcommand_matches("odx") {
            let values: Vec<_> = matches.values_of("number")
                .unwrap().collect();
            odx(&values);
        }
    } else if matches.is_present("cmd") {
        if let Some(matches) = matches.subcommand_matches("cmd") {
            let command = matches.value_of("command").unwrap();
            let items: Vec<_> = matches.values_of("items")
                .unwrap().collect();
            cmd(command, &items);
        }
    } else if matches.is_present("rename") {
        println!("Work needed for rename");
        rename();
    } else if matches.is_present("range") {
        println!("Work needed for range");
        range();
    } else if matches.is_present("xargs") {
        println!("Work needed for xargs");
        xargs();
    }
}

// Display the ascii code table
fn ascii() {
    let mut line = String::from("");
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
        println!("{}", line);
        line = String::from("");
        ldx += 8;
    }
}

// Report each value in the array in hex, decimal, octal, and binary format
fn odx(values: &[&str]) {
    println!("values to convert: {:?}", values);
}

// Run *command* once for each element in *items*, with the '%' in
// command replaced with the element
fn cmd(command: &str, items: &[&str]) {
    println!("cmd('{}', {:?})", command, items);
}

// desc
fn rename() {
}

// desc
fn range() {
}

// desc
fn xargs() {
}


