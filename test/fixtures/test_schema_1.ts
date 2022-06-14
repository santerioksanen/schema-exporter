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

export interface Root {
  nested_leaf_1?: Leaf;
  nested_leaf_2?: Leaf[];
  list_leaf_1?: Leaf[];
  test_enum_1?: TestEnum1;
  test_enum_2?: TestEnum2[];
}
