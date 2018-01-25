extern crate clap;
extern crate regex;
use clap::{App, AppSettings, SubCommand, Arg};
use std::error::Error;
use std::fs::File;
use std::io::prelude::*;
use std::path::Path;
use std::process::Command;

mod ascii;
mod cmd;
mod mag;
mod odx;
mod perrno;
mod range;
mod rename;
mod xargs;

// ----------------------------------------------------------------------------
// This is the single source of truth for the project's version value.
//
fn version() -> &'static str {
    "0.0.6"
}

// ----------------------------------------------------------------------------
// This is the main entrypoint.
//
fn main() {
    let mut app = App::new("fx").version(version())
        .author("Tom Barron <tusculum@gmail.com>")
        .about("Command line effects ( fx, get it? ;)")
        .setting(AppSettings::VersionlessSubcommands)
        .subcommand(SubCommand::with_name("ascii")
                    .about("show the ascii code table")
        )
        .subcommand(SubCommand::with_name("cmd")
                    .about("replace % with arguments")
                    .arg(Arg::with_name("dryrun")
                         .help("report what would happen without acting")
                         .short("n")
                         .long("dryrun")
                    )
                    .arg(Arg::with_name("verbose")
                         .help("show command before running it")
                         .short("v")
                         .long("verbose")
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
                    .arg(Arg::with_name("binary")
                         .help("Use divisor 1024")
                         .short("b")
                         .long("binary")
                    )
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
                    .about("report errno values and meanings")
                    .arg(Arg::with_name("name_or_number")
                         .help("errno number or name")
                         .required(true)
                         .min_values(1)
                    )
        )
        .subcommand(SubCommand::with_name("range")
                    .about("replace % in command with numbers from <interval>")
                    .arg(Arg::with_name("dryrun")
                         .help("Report what would happen without acting")
                         .short("n")
                         .long("dryrun")
                    )
                    .arg(Arg::with_name("verbose")
                         .help("Show command before running it")
                         .short("v")
                         .long("verbose")
                    )
                    .arg(Arg::with_name("command")
                         .help("string with '%'")
                         .required(true)
                    )
                    .arg(Arg::with_name("lohigh")
                         .help("<low>..<high> range from <low> to <high>-1")
                         .value_name("interval")
                         .short("i")
                         .long("interval")
                         .required(true)
                         .takes_value(true)
                    )
                    .arg(Arg::with_name("zeropad")
                         .help("Zero fill to <zeropad> columns")
                         .value_name("zeropad")
                         .short("z")
                         .long("zpad")
                         .takes_value(true)
                    )
        )
        .subcommand(SubCommand::with_name("rename")
                    .about("Rename files based on a s/foo/bar/ expr")
                    .arg(Arg::with_name("dryrun")
                         .short("n")
                         .long("dryrun")
                         .help("Report what would happen without acting")
                    )
                    .arg(Arg::with_name("verbose")
                         .short("v")
                         .long("verbose")
                         .help("Report renames as they happen")
                    )
                    .arg(Arg::with_name("substitute")
                         .help("Edit expression: s/old/new/")
                         .required(true)
                    )
                    .arg(Arg::with_name("items")
                         .help("Files to rename")
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
            let command = matches.value_of("command").unwrap();
            let items: Vec<_> = matches.values_of("items")
                .unwrap().collect();
            let dryrun = matches.is_present("dryrun");
            let verbose = matches.is_present("verbose");
            cmd::cmd(dryrun, verbose, command, &items);
        }
    } else if matches.is_present("mag") {
        if let Some(matches) = matches.subcommand_matches("mag") {
            let values: Vec<_> = matches.values_of("number")
                .unwrap().collect();
            let binary = matches.is_present("binary");
            mag::mag(binary, &values);
        }
    } else if matches.is_present("odx") {
        if let Some(matches) = matches.subcommand_matches("odx") {
            let values: Vec<_> = matches.values_of("number")
                .unwrap().collect();
            odx::odx(&values);
        }
    } else if matches.is_present("perrno") {
        if let Some(matches) = matches.subcommand_matches("perrno") {
            let values: Vec<_> = matches.values_of("name_or_number")
                .unwrap().collect();
            perrno::perrno(&values);
        }
    } else if matches.is_present("range") {
        if let Some(matches) = matches.subcommand_matches("range") {
            let command = matches.value_of("command").unwrap();
            let lohigh = matches.value_of("lohigh").unwrap();
            let zpad: usize = match matches.value_of("zeropad") {
                Some(x) => x.parse().unwrap(),
                None => 0,
            };
            let dryrun = matches.is_present("dryrun");
            let verbose = matches.is_present("verbose");
            range::range(dryrun, verbose, command, lohigh, zpad);
        }
    } else if matches.is_present("rename") {
        if let Some(matches) = matches.subcommand_matches("rename") {
            let dryrun = matches.is_present("dryrun");
            let verbose = matches.is_present("verbose");
            let subst = matches.value_of("substitute").unwrap();
            let items: Vec<_> = matches.values_of("items").unwrap().collect();
            rename::rename(dryrun, verbose, subst, items);
        }
    } else if matches.is_present("xargs") {
        println!("Work needed for xargs");
        xargs::xargs();
    } else {
        println!("A subcommand is required.\n");
        app.print_help().expect("print failure");
        println!("");
    }
}

// ----------------------------------------------------------------------------
// Read the version value out of file Cargo.toml so we can verify that
// it's correct.
//
fn _get_cargo_version() -> String {
    let content = read_file("Cargo.toml");
    let mut rval = String::new();
    for line in content.lines() {
        if line.contains("version") {
            let pieces: Vec<&str> = line.split("\"").collect();
            rval.push_str(pieces[1]);
            break;
        }
    }
    rval
}

// ----------------------------------------------------------------------------
// Read the version value out of file Cargo.toml so we can verify that
// it's correct.
//
fn read_file(filename: &str) -> String {
    let path = Path::new(filename);
    let display = path.display();
    let mut file = match File::open(&path) {
        Err(why) => panic!("couldn't open {}: {}",
                           display,
                           why.description()),
        Ok(file) => file,
    };

    let mut content: String = String::new();
    match file.read_to_string(&mut content) {
        Err(why) => panic!("couldn't read {}: {}",
                           display,
                           why.description()),
        Ok(_num) => (),
    }
    content
}

// ----------------------------------------------------------------------------
// Given a String, attempt to parse it into a 32 bit int. If the parse
// operation fails, return the default value.
//
fn str_to_int32(value: &str, default: i32) -> i32 {
    let rval: i32 = match value.parse() {
        Ok(num) => num,
        Err(_)  => default
    };
    rval
}

// ----------------------------------------------------------------------------
// Given a String, treat it as a command try to run it.
//
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
// Given a String, report it as something we would do if we didn't
// have --dryrun on the command line.
//
fn would_do(cmd: &String) {
    println!("would do '{}'", cmd);
}

// ----------------------------------------------------------------------------
// Module tests
//
#[cfg(test)]
mod tests {
    use super::*;

    // ------------------------------------------------------------------------
    // Verify that the locally defined project version match the value
    // in Cargo.toml or fail
    //
    #[test]
    fn test_cargo_version() {
        assert_eq!(version(), _get_cargo_version());
    }
}
