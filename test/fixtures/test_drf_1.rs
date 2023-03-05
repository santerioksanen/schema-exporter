use chrono::{DateTime, Utc};
use rust_decimal::Decimal;
use serde_derive::{Deserialize, Serialize};
use strum_macros::{AsStaticStr, Display, EnumString};

#[derive(AsStaticStr, Clone, Copy, Debug, Deserialize, Display, EnumString, Serialize)]
pub enum TestEnum1 {
    A,
    B,
    C,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Leaf {
    pub bool_1: bool,
    pub datetime_1: DateTime<Utc>,
    pub decimal_1: Decimal,
    pub int_1: i64,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Leaf2 {
    pub datetime_1: Option<DateTime<Utc>>,
    pub integer_1: Option<i64>,
    pub many_1: Vec<String>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Middle {
    pub test_enum_1: TestEnum1,
    pub leaf_schema: Leaf,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Root2 {
    pub nested_leaf_1: Leaf2,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Root {
    pub nested_leaf_1: Middle,
    pub nested_leaf_2: Vec<Middle>,
    pub list_leaf_1: Vec<Middle>,
}
