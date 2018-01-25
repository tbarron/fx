use std::fs;

// ----------------------------------------------------------------------------
// Rename a list of items based on a substitute expression
//
pub fn rename(dryrun: bool, verbose: bool, subst: &str, items: Vec<&str>) {
    let tup = parse_substitute(subst);
    if dryrun && verbose {
        println!("--dryrun and --verbose together don't make sense");
    } else if dryrun {
        for item in items {
            let target = item.replace(tup.0, tup.1);
            if item == target {
                println!("Would not rename {} -- no change", item);
            } else {
                println!("Would rename {} to {}", item, target);
            }
        }
    } else {
        for item in items {
            let target = item.replace(tup.0, tup.1);
            if item == target {
                if verbose {
                    println!("Not renaming {} -- no change", item);
                }
            } else {
                if verbose {
                    println!("Renaming {} to {}", item, target);
                }
                fs::rename(item, target).unwrap();
            }
        }
    }
}

// ----------------------------------------------------------------------------
// Parse out the pieces of the substitute expression
//
fn parse_substitute(subst: &str) -> (&str, &str) {
    let sep = subst.chars().nth(1).unwrap();
    let pieces: Vec<&str> = subst.split(sep).collect();
    (pieces[1], pieces[2])
}
