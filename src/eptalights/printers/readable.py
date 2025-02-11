from eptalights.printers.base import PrettyPrinterBase
import re


class ReadablePrettyPrinter(PrettyPrinterBase):
    @property
    def RSPACE(cls):
        # return "    "
        return " "

    def print_expr_model(cls, obj):
        if obj.rhs is not None:
            return (
                f"expr_type:{obj.expr_type.value}, "
                f"lhs:{obj.lhs.print()}, "
                f"rhs:{obj.rhs.print()}"
            )
        else:
            return f"expr_type:{obj.expr_type.value}, " f"lhs:{obj.lhs.print()}"

    def print_egimple_ir_nop_model(cls, obj):
        return (
            f"EGimpleIRNopModel <"
            f"step_index={obj.step_index},"
            f"{cls.RSPACE}lowlevel_steps={obj.low_level_steps}"
            ">"
        )

    def print_egimple_ir_assign_model(cls, obj):
        exp_str = obj.src.print()
        return (
            f"EGimpleIRAssignModel <"
            f"step_index={obj.step_index},"
            f"{cls.RSPACE}lowlevel_steps={obj.low_level_steps},"
            f"{cls.RSPACE}dst={obj.dst.print()}"
            f"{cls.RSPACE}src={exp_str} "
            ">"
        )

    def print_egimple_ir_call_model(cls, obj):
        fargs_str = f"{cls.RSPACE}fargs=["
        for idx, arg in enumerate(obj.fargs):
            if idx == 0:
                fargs_str += f"{idx}={arg.print()}"
            else:
                fargs_str += f",{cls.RSPACE}{cls.RSPACE}{idx}={arg.print()}"
        fargs_str += "]"

        dst_str = "None"
        if obj.dst:
            dst_str = obj.dst.print()

        return (
            f"EGimpleIRCallModel <"
            f"step_index={obj.step_index},"
            f"{cls.RSPACE}lowlevel_steps={obj.low_level_steps},"
            f"{cls.RSPACE}fname={obj.fname},"
            f"{cls.RSPACE}dst={dst_str}"
            f"{fargs_str}"
            ">"
        )

    def print_egimple_ir_cond_model(cls, obj):
        exp_str = obj.src.print()
        return (
            f"EGimpleIRCondModel <"
            f"step_index={obj.step_index},"
            f"{cls.RSPACE}lowlevel_steps={obj.low_level_steps},"
            f"{cls.RSPACE}src={exp_str},"
            f"{cls.RSPACE}true_dst_block_index={obj.true_dst_block_index} "
            f"{cls.RSPACE}false_dst_block_index={obj.false_dst_block_index}"
            ">"
        )

    def print_egimple_ir_return_model(cls, obj):
        if obj.dst is not None:
            return (
                f"EGimpleIRReturnModel <"
                f"step_index={obj.step_index},"
                f"{cls.RSPACE}lowlevel_steps={obj.low_level_steps},"
                f"{cls.RSPACE}dst={obj.dst.print()}"
                ">"
            )
        else:
            return (
                f"EGimpleIRReturnModel <"
                f"step_index={obj.step_index},"
                f"{cls.RSPACE}lowlevel_steps={obj.low_level_steps}"
                ">"
            )

    def print_egimple_ir_goto_model(cls, obj):
        if obj.dst_block_index is not None:
            return (
                f"EGimpleIRGotoModel <"
                f"step_index={obj.step_index},"
                f"{cls.RSPACE}lowlevel_steps={obj.low_level_steps},"
                f"{cls.RSPACE}dst={obj.dst_block_index}"
                ">"
            )
        else:
            return "EGimpleIRGotoModel <>\n"

    def print_egimple_ir_switch_model(cls, obj):
        pass

    def print_function_model(cls, obj):
        fn_str = ""
        for bb_idx, step_index_list in obj.cfg.basicblock_steps.items():
            fn_str += f"<bb {bb_idx}> :\n"
            for step_index in step_index_list:
                fn_str += obj.steps[step_index].print() + "\n"
        return fn_str

    def print_tokenized_operand_model(cls, obj, max_length: int = 100):
        def _is_number(s):
            try:
                float(s)  # float() can handle both integers and floats
                return True
            except ValueError:
                return False

        tstr = ""
        for t in obj.tokens:
            cleaned_string = re.sub(r"[\n\t]", "", t.value)
            # Limit the string to the specified length
            if len(cleaned_string) > max_length:
                cleaned_string = cleaned_string[:max_length]
                cleaned_string = cleaned_string + "..."

            if t.token_type.value == "IS_CONSTANT" and not _is_number(cleaned_string):
                tstr += '"' + cleaned_string + '"'
            else:
                tstr += cleaned_string

        return tstr
