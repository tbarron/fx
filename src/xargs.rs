use super::*;

// ----------------------------------------------------------------------------
// This function reads tokens from stdin and inserts them into
// *command* where the '%' is, limiting the total length of command
// lines to around 250 bytes. With *dryrun*, just report the generated
// commands without actually running them. With *verbose*, report the
// generated commands before running each one.
//
pub fn xargs(dryrun: bool, verbose: bool, command: &str) {
    println!("dryrun = {:?}", dryrun);
    println!("verbose = {:?}", verbose);
    println!("command = '{}'", command);

    let stdin = read_file("<stdin>");
    println!("{}", stdin);
}
