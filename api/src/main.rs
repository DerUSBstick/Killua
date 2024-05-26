#[macro_use] extern crate rocket;
use rocket::{routes, fairing::AdHoc};
use rocket::serde::Deserialize;
use std::sync::Arc;

// add routes module
mod routes;
mod fairings;
#[cfg(test)] mod tests;

// import routes
use routes::commands::get_commands;
use routes::vote::register_vote;
use routes::stats::get_stats;
use routes::image::image;
use routes::diagnostics::get_diagnostics;

use fairings::cors::Cors;
use fairings::counter::Counter;
use fairings::timer::RequestTimer;

#[derive(Deserialize)]
#[serde(crate = "rocket::serde")]
pub struct Config {
    api_key: String,
}

#[launch]
fn rocket() -> _ {
    let counter = Arc::new(Counter::default());
    rocket::build()
        .mount("/", routes![get_commands, register_vote, get_stats, image, get_diagnostics])
        .attach(AdHoc::config::<Config>())
        .attach(Cors)
        .manage(Arc::clone(&counter))
        .attach(counter)
        .attach(RequestTimer)
}
