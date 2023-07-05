export enum TestEnum1 {
  A = "a",
  B = "b",
  C = "c",
}

export interface Leaf {
  bool_1: boolean
  datetime_1: string
  decimal_1: number
  int_1: number
}

export interface Leaf2 {
  datetime_1?: string
  integer_1?: number
  many_1: string[]
}

export interface Middle {
  test_enum_1: TestEnum1
  leaf_schema: Leaf
}

export interface Root2 {
  nested_leaf_1: Leaf2
}

export interface Root {
  nested_leaf_1: Middle
  nested_leaf_2: Middle[]
  list_leaf_1: Middle[]
}
