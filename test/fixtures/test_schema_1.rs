use chrono::{DateTime, Utc};
use rust_decimal::Decimal;
use serde::{Deserialize, Serialize};
use strum_macros::EnumString;

#[derive(Clone, Copy, Debug, Deserialize, EnumString, Serialize)]
pub enum TestEnum1 {
    A,
    B,
    C,
}

#[derive(Clone, Copy, Debug, Deserialize, EnumString, Serialize)]
pub enum TestEnum2 {
    A,
    B,
    C,
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
pub struct Leaf {
    pub bool_1: Option<bool>,
    pub boolean_1: Option<bool>,
    pub datetime_1: Option<DateTime<Utc>>,
    pub decimal_1: Option<Decimal>,
    pub int_1: Option<i64>,
    pub integer_1: Option<i64>,
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
pub struct Root {
    pub nested_leaf_1: Option<Leaf>,
    pub nested_leaf_2: Option<Vec<Leaf>>,
    pub list_leaf_1: Option<Vec<Leaf>>,
    pub test_enum_1: Option<TestEnum1>,
    pub test_enum_2: Option<Vec<TestEnum2>>,
}
