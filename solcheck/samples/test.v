Lemma example1 : forall a: nat, a + 0 = a.
  induction a.
  - simpl. reflexivity.
  - simpl. rewrite IHa. reflexivity.
Qed.
