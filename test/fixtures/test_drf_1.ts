export interface Leaf {
  bool_1: boolean;
  datetime_1: Date;
  decimal_1: number;
  int_1: number;
}

export interface Leaf2 {
  datetime_1?: Date;
  integer_1?: number;
  many_1: string[];
}

export interface Middle {
  leaf_schema: Leaf;
}

export interface Root2 {
  nested_leaf_1: Leaf2;
}

export interface Root {
  nested_leaf_1: Middle;
  nested_leaf_2: Middle[];
  list_leaf_1: Middle[];
}
