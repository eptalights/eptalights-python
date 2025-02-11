class PrettyPrinterBase:
    def print_expr_model(cls, obj):
        raise NotImplementedError

    def print_egimple_ir_nop_model(cls, obj):
        raise NotImplementedError

    def print_egimple_ir_assign_model(cls, obj):
        raise NotImplementedError

    def print_egimple_ir_call_model(cls, obj):
        raise NotImplementedError

    def print_egimple_ir_cond_model(cls, obj):
        raise NotImplementedError

    def print_egimple_ir_return_model(cls, obj):
        raise NotImplementedError

    def print_egimple_ir_goto_model(cls, obj):
        raise NotImplementedError

    def print_egimple_ir_switch_model(cls, obj):
        raise NotImplementedError

    def print_function_model(cls, obj):
        raise NotImplementedError

    def print_tokenized_operand_model(cls, obj):
        raise NotImplementedError

    def print_expr_type(cls, obj):
        raise NotImplementedError
