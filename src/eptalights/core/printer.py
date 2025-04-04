from eptalights.printers.pseudo_c import PseudoCPrettyPrinter

# from eptalights.printers.pseudo_c import PseudoCPrettyPrinterColored


DEFAULT_PRETTY_PRINTER = "pseudo_c"

PRETTY_PRINTER_REGISTRY = {
    "pseudo_c": PseudoCPrettyPrinter,
    # "pseudo_c_with_syntax_highlight": PseudoCPrettyPrinterWithSyntaxHighlight,
}


class PrettyPrinter:
    @staticmethod
    def decompile(obj_instance):
        typename: str = type(obj_instance).__name__
        printer = PRETTY_PRINTER_REGISTRY.get(DEFAULT_PRETTY_PRINTER)

        match typename:
            case "ExprModel":
                return printer.print_expr_model(obj_instance)

            case "EGimpleIRNopModel":
                return printer.print_egimple_ir_nop_model(obj_instance)

            case "EGimpleIRAssignModel":
                return printer.print_egimple_ir_assign_model(obj_instance)

            case "EGimpleIRCallModel":
                return printer.print_egimple_ir_call_model(obj_instance)

            case "EGimpleIRCondModel":
                return printer.print_egimple_ir_cond_model(obj_instance)

            case "EGimpleIRReturnModel":
                return printer.print_egimple_ir_return_model(obj_instance)

            case "EGimpleIRGotoModel":
                return printer.print_egimple_ir_goto_model(obj_instance)

            case "EGimpleIRSwitchModel":
                return printer.print_egimple_ir_switch_model(obj_instance)

            case "EGimpleIRLabelModel":
                return printer.print_egimple_ir_label_model(obj_instance)

            case "FunctionModel":
                return printer.print_function_model(obj_instance)

            case "TokenizedOperandModel":
                return printer.print_tokenized_operand_model(obj_instance)

            case "ExprType":
                return printer.print_expr_type(obj_instance)

            case "VariableModel":
                return printer.print_variable_model(obj_instance)

            case "FileDataModel":
                return printer.print_file_data_model(obj_instance)

            case _:
                return f"<<No Printer - {typename}>>"
