from eptalights.printers.base import PrettyPrinterBase
import re

RSPACE = " "
DSPACE = "\t"


def simplify_demangled(demangled: str) -> str:
    return demangled


class PseudoCPrettyPrinter(PrettyPrinterBase):
    @classmethod
    def print_expr_model(cls, obj):
        if obj.rhs is not None:
            return (
                f"{obj.lhs.decompile()} "
                f"{obj.expr_type.decompile()} "
                f"{obj.rhs.decompile()}"
            )
        else:
            if obj.expr_type.value == "BITWISE_NOT_EXPR":
                return f"!{obj.lhs.decompile()}"
            else:
                return f"{obj.lhs.decompile()}"

    @classmethod
    def print_egimple_ir_nop_model(cls, obj):
        return f"{DSPACE}nop;\n"

    @classmethod
    def print_egimple_ir_assign_model(cls, obj):
        exp_str = obj.src.decompile()
        return f"{DSPACE}{obj.dst.decompile()} = {exp_str};\n"

    @classmethod
    def print_egimple_ir_call_model(cls, obj):
        fargs_str = " ( "
        for idx, arg in enumerate(obj.fargs):
            if idx == 0:
                fargs_str += f"{simplify_demangled(arg.decompile())}"
            else:
                fargs_str += f", {simplify_demangled(arg.decompile())}"
        fargs_str += " )"

        dst_str = None
        if obj.dst:
            dst_str = simplify_demangled(obj.dst.decompile())
            return f"{DSPACE}{dst_str} = {simplify_demangled(obj.fname)} {fargs_str};\n"
        else:
            return f"{DSPACE}{simplify_demangled(obj.fname)} {fargs_str};\n"

    # @classmethod
    # def print_egimple_ir_call_model_stdout(cls, obj):
    #     dst_str = ""
    #     if obj.dst:
    #         dst_str = obj.dst.decompile()

    #     fargs_str = f""
    #     for idx, arg in enumerate(obj.fargs):
    #         if idx == 0:
    #             fargs_str += f"{idx}={arg.decompile()}"
    #         else:
    #             fargs_str += f",{cls.RSPACE}{cls.RSPACE}{idx}={arg.decompile()}"
    #     fargs_str += f"]"

    #     return f"{dst_str} = {obj.fname} ()"

    @classmethod
    def print_egimple_ir_cond_model(cls, obj):
        exp_str = obj.src.decompile()
        return (
            f"{DSPACE}if ( {exp_str} )\n"
            f"{DSPACE}{DSPACE}goto <bb {obj.true_dst_block_index}>;\n"
            f"{DSPACE}else\n"
            f"{DSPACE}{DSPACE}goto <bb {obj.false_dst_block_index}>;\n"
        )

    @classmethod
    def print_egimple_ir_return_model(cls, obj):
        if obj.dst is not None:
            return f"{DSPACE}return {obj.dst.decompile()};\n"
        else:
            return f"{DSPACE}return;\n"

    @classmethod
    def print_egimple_ir_goto_model(cls, obj):
        if obj.dst_block_index is not None:
            return f"{DSPACE}goto {obj.dst_block_index};\n"
        else:
            return f"{DSPACE}goto <>;\n"

    @classmethod
    def print_egimple_ir_switch_model(cls, obj):
        switch_str = f"{DSPACE}switch ( {obj.switch_index.decompile()} )\n"

        for i, case in enumerate(obj.switch_cases):
            switch_str = switch_str + (
                f"{DSPACE}case {case.decompile()} :\n"
                f"{DSPACE}{DSPACE}goto <bb {obj.switch_basic_blocks[i]}>;\n"
            )
        return switch_str

    @classmethod
    def print_function_model(cls, obj):
        fn_str = "\n"

        if obj.class_name is not None:
            fn_str = fn_str + obj.class_name + " :: " + obj.name
        else:
            fn_str = fn_str + obj.name

        fn_args_str = "  ( "
        fn_args_str = fn_args_str + ", ".join(obj.variable_manager.function_args)
        fn_args_str = fn_args_str + " )"

        fn_str = fn_str + fn_args_str + "\n{\n"

        for bb_idx, step_index_list in obj.cfg.basicblock_steps.items():
            fn_str += f"\n\t<bb {bb_idx}> :\n"

            for step_index in step_index_list:
                fn_str += obj.steps[step_index].decompile()

        fn_str += "\n}\n"
        return fn_str

    @classmethod
    def print_tokenized_operand_model(cls, obj):
        def _is_number(s):
            try:
                float(s)  # float() can handle both integers and floats
                return True
            except ValueError:
                return False

        tstr = ""
        for t in obj.tokens:
            if t.value_extended is not None:
                tstr += t.value_extended
                continue

            cleaned_string = re.sub(r"[\n\t]", "", t.value)

            if t.token_type.value == "IS_CONSTANT" and not _is_number(cleaned_string):
                tstr += 'R"(' + cleaned_string + ')"'
            else:
                tstr += cleaned_string

        return tstr

    @classmethod
    def print_expr_type(cls, obj):
        if obj == obj.NO_EXPR:
            return ""

        if obj == obj.MULT_EXPR:
            return "*"

        if obj == obj.PLUS_EXPR:
            return "+"

        if obj == obj.MINUS_EXPR:
            return "-"

        if obj == obj.RDIV_EXPR:
            return "/"

        if obj == obj.MOD_EXPR:
            return "%"

        if obj == obj.DIV_EXPR:
            return "/"

        if obj == obj.GREATER_THAN_OR_EQUAL_EXPR:
            return ">="

        if obj == obj.GREATER_THAN_EXPR:
            return ">"

        if obj == obj.LESS_THAN_EXPR:
            return "<"

        if obj == obj.LESS_THAN_OR_EQUAL_EXPR:
            return "<="

        if obj == obj.EQUAL_EXPR:
            return "=="

        if obj == obj.NOT_EQUAL_EXPR:
            return "!="

        if obj == obj.BITWISE_AND_EXPR:
            return "&&"

        if obj == obj.BITWISE_EXCLUSIVE_OR_EXPR:
            return "&"

        if obj == obj.BITWISE_INCLUSIVE_OR_EXPR:
            return "|"

        if obj == obj.BITWISE_NOT_EXPR:
            return "~"

        if obj == obj.TRUNC_DIV_EXPR:
            return "/"

        if obj == obj.TRUNC_MOD_EXPR:
            return "%"

        if obj == obj.LSHIFT_EXPR:
            return "<<"

        if obj == obj.RSHIFT_EXPR:
            return ">>"

        if obj == obj.RROTATE_EXPR:
            return "RROTATE_EXPR"

        if obj == obj.NEGATE_EXPR:
            return "~"

        if obj == obj.MIN_EXPR:
            return "<"

        if obj == obj.MAX_EXPR:
            return ">"

        if obj == obj.POINTER_PLUS_EXPR:
            return "+"

        if obj == obj.FIX_TRUNC_EXPR:
            return "FIX_TRUNC_EXPR"

        if obj == obj.UNDEF:
            return "UNDEF"

        return
