extern crate clap;
use clap::{App, SubCommand, Arg};

mod ascii;
mod mag;
mod odx;

// ----------------------------------------------------------------------------
fn version() -> &'static str {
    "0.0.2"
}

fn main() {
    let mut app = App::new("fx").version("0.0.1")
        .author("Tom Barron <tusculum@gmail.com>")
        .about("Command line effects (fx, get it?)")
        .subcommand(SubCommand::with_name("ascii")
                    .about("show the ascii code table")
                       )
        .subcommand(SubCommand::with_name("cmd")
                    .about("replace % with arguments (needs work)")
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
                    .about("report the size of a number (needs work)")
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
                    .about("replace % in command with nums from range \
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
                    .arg(Arg::with_name("lohigh")
                         .short("i")
                         .help("low:high range from low to high-1")
                         .required(true)
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
            let command = matches.value_of("command").unwrap();
            let items: Vec<_> = matches.values_of("items")
                .unwrap().collect();
            cmd(command, &items);
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
        println!("Work needed for range");
        range();
    } else if matches.is_present("rename") {
        println!("Work needed for rename");
        rename();
    } else if matches.is_present("xargs") {
        println!("Work needed for xargs");
        xargs();
    } else {
        println!("    A subcommand is required.\n");
        app.print_help().expect("print failure");
        println!("");
    }
}

// ----------------------------------------------------------------------------
// Run *command* once for each element in *items*, with the '%' in
// command replaced with the element
fn cmd(command: &str, items: &[&str]) {
    println!("cmd('{}', {:?})", command, items);
}

// ----------------------------------------------------------------------------
// Apply a substitute expression to a set of file names and possibly
// rename the files
fn rename() {
}

// ----------------------------------------------------------------------------
// desc
fn range() {
}

// ----------------------------------------------------------------------------
// desc
fn xargs() {
}


