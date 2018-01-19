extern crate clap;
use clap::{App, SubCommand, Arg};
use std::error::Error;
use std::fs::File;
use std::io::prelude::*;
use std::path::Path;
use std::process::Command;

mod ascii;
mod cmd;
mod mag;
mod odx;
mod range;

// ----------------------------------------------------------------------------
fn version() -> &'static str {
    "0.0.3"
}

// ----------------------------------------------------------------------------
fn main() {
    let mut app = App::new("fx").version(version())
        .author("Tom Barron <tusculum@gmail.com>")
        .about("Command line effects (fx, get it?)")
        .subcommand(SubCommand::with_name("ascii")
                    .about("show the ascii code table")
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
        .subcommand(SubCommand::with_name("mag")
                    .about("report the size of a number")
                    .arg(Arg::with_name("number")
                         .help("values to be assessed")
                         .required(true)
                         .min_values(1)
                        )
                    )
        .subcommand(SubCommand::with_name("odx")
                    .about("report hex, octal, binary values")
                        .arg(Arg::with_name("number")
                             .help("value to convert")
                             .required(true)
                             .min_values(1)
                            )
                       )
        .subcommand(SubCommand::with_name("perrno")
                    .about("report errno values and meanings (needs work)")
                   )
        .subcommand(SubCommand::with_name("range")
                    .about("replace % in command with nums from range")
                    .arg(Arg::with_name("dryrun")
                         .short("n")
                         .long("dryrun")
                         .help("report what would happen without acting")
                        )
                    .arg(Arg::with_name("rcmd")
                         .help("string with '%'")
                         .required(true)
                        )
                    .arg(Arg::with_name("lohigh")
                         .help("low:high range from low to high-1")
                         .value_name("interval")
                         .short("i")
                         .long("interval")
                         .required(true)
                         .takes_value(true)
                        )
                    .arg(Arg::with_name("zeropad")
                         .help("zero fill to N columns")
                         .value_name("zeropad")
                         .short("z")
                         .long("zpad")
                         .required(true)
                         .takes_value(true)
                        )
                   )
        .subcommand(SubCommand::with_name("rename")
                    .about("rename files based on a s/foo/bar/ expr \
                            (needs work)")
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
        .subcommand(SubCommand::with_name("xargs")
                    .about("replace % in command with clumps of args \
                            (needs work)")
                    .arg(Arg::with_name("dryrun")
                         .short("n")
                         .long("dryrun")
                         .help("report what would happen without acting")
                        )
                    .arg(Arg::with_name("command")
                         .help("string with '%'")
                         .required(true)
                        )
                   );
    let matches = app.clone().get_matches();

    if matches.is_present("ascii") {
        ascii::ascii();
    } else if matches.is_present("cmd") {
        if let Some(matches) = matches.subcommand_matches("cmd") {
            let dryrun = matches.is_present("dryrun");
            let command = matches.value_of("command").unwrap();
            let items: Vec<_> = matches.values_of("items")
                .unwrap().collect();
            cmd::cmd(dryrun, command, &items);
        }
    } else if matches.is_present("mag") {
        if let Some(matches) = matches.subcommand_matches("mag") {
            let values: Vec<_> = matches.values_of("number")
                .unwrap().collect();
            mag::mag(&values);
        }
    } else if matches.is_present("odx") {
        if let Some(matches) = matches.subcommand_matches("odx") {
            let values: Vec<_> = matches.values_of("number")
                .unwrap().collect();
            odx::odx(&values);
        }
    } else if matches.is_present("range") {
        if let Some(matches) = matches.subcommand_matches("range") {
            let dryrun = matches.is_present("dryrun");
            let rcmd = matches.value_of("rcmd").unwrap();
            let lohigh = matches.value_of("lohigh").unwrap();
            let zpad: usize = matches.value_of("zeropad").unwrap().parse().unwrap();
            range::range(dryrun, rcmd, lohigh, zpad);
        }
    } else if matches.is_present("rename") {
        println!("Work needed for rename");
        rename();
    } else if matches.is_present("xargs") {
        println!("Work needed for xargs");
        xargs();
    } else {
        println!("A subcommand is required.\n");
        app.print_help().expect("print failure");
        println!("");
    }
}

// ----------------------------------------------------------------------------
// Apply a substitute expression to a set of file names and possibly
// rename the files
fn rename() {
}

// ----------------------------------------------------------------------------
// desc
fn xargs() {
}

// ----------------------------------------------------------------------------
fn _get_cargo_version() -> String {
    let path = Path::new("Cargo.toml");
    let display = path.display();
    let mut file = match File::open(&path) {
        Err(why) => panic!("couldn't open {}: {}",
                           display,
                           why.description()),
        Ok(file) => file,
    };

    let mut s: String = String::new();
    match file.read_to_string(&mut s) {
        Err(why) => panic!("couldn't read {}: {}",
                           display,
                           why.description()),
        Ok(_num) => (),
    }

    let mut rval = String::new();
    for line in s.lines() {
        if line.contains("version") {
            let pieces: Vec<&str> = line.split("\"").collect();
            rval.push_str(pieces[1]);
            break;
        }
    }
    rval
}

// ----------------------------------------------------------------------------
fn would_do(cmd: &String) {
    println!("would do '{}'", cmd);
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
    fn test_cargo_version() {
        assert_eq!(version(), _get_cargo_version());
    }
}
