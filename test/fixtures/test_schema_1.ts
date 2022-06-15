export enum TestEnum1 {
  A = "a",
  B = "b",
  C = "c",
}

export enum TestEnum2 {
  A = 1,
  B = 2,
  C = 3,
}

export interface Leaf {
  bool_1?: boolean;
  boolean_1?: boolean;
  datetime_1?: Date;
  decimal_1?: number;
  int_1?: number;
  integer_1?: number;
}

export interface Leaf2 {
  datetime_1: Date;
  decimal_1: number;
}

export interface Middle {
  test_enum_2?: TestEnum2[];
  leaf_schema?: Leaf;
}

export interface Root2 {
  nested_leaf_1: Leaf2;
}

export interface Root {
  nested_leaf_1?: Middle;
  nested_leaf_2?: Middle[];
  list_leaf_1?: Middle[];
  test_enum_1?: TestEnum1;
}
