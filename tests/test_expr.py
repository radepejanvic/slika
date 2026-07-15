import os
import numpy as np
import cv2
import pytest
from pathlib import Path
from textx import metamodel_from_file

from engine.engine import Engine
from engine.expr import evaluate_expr


GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "grammar", "slika.tx")


def parse(program_text, tmp_path):
    """Parses a full .sl program string and returns the textX model."""
    program_path = Path(tmp_path) / "test_program.sl"
    program_path.write_text(program_text)
    metamodel = metamodel_from_file(GRAMMAR_PATH)
    return metamodel.model_from_file(str(program_path))


def parse_expr(expr_text, tmp_path):
    """Parses 'let k = <expr_text>' and returns the resulting Expr AST node."""
    model = parse(f"let k = {expr_text}\n", tmp_path)
    return model.statements[0].value


def run_program(program_text, tmp_path, backend):
    """Parses and runs a full .sl program, returning the Engine used."""
    model = parse(program_text, tmp_path)
    engine = Engine(backend)
    engine.interpret(model)
    return engine


# ---------- Grammar: Let / Expr parsing ----------

def test_let_parses_integer_literal(tmp_path):
    """Tests that 'let x = 5' parses into a Let statement."""
    model = parse("let x = 5\n", tmp_path)
    stmt = model.statements[0]
    assert stmt.__class__.__name__ == "Let"
    assert stmt.name == "x"


def test_let_is_a_valid_top_level_statement(tmp_path):
    """Tests that Let can be freely mixed with other statements."""
    model = parse("let k = 5\nlet m = k\n", tmp_path)
    assert [s.__class__.__name__ for s in model.statements] == ["Let", "Let"]


def test_expr_parses_addition(tmp_path):
    expr = parse_expr("1 + 2", tmp_path)
    assert evaluate_expr(expr, {}) == 3


def test_expr_parses_subtraction(tmp_path):
    expr = parse_expr("5 - 2", tmp_path)
    assert evaluate_expr(expr, {}) == 3


def test_expr_parses_multiplication(tmp_path):
    expr = parse_expr("4 * 3", tmp_path)
    assert evaluate_expr(expr, {}) == 12


def test_expr_parses_division(tmp_path):
    expr = parse_expr("10 / 4", tmp_path)
    assert evaluate_expr(expr, {}) == 2.5


def test_expr_parses_parenthesized_group(tmp_path):
    expr = parse_expr("(1 + 2)", tmp_path)
    assert evaluate_expr(expr, {}) == 3


def test_expr_parses_nested_parentheses(tmp_path):
    expr = parse_expr("((1 + 2) * (3 + 1))", tmp_path)
    assert evaluate_expr(expr, {}) == 12


# ---------- Evaluator: precedence & associativity ----------

def test_multiplication_binds_tighter_than_addition(tmp_path):
    """2 + 3 * 4 should be 14, not 20."""
    expr = parse_expr("2 + 3 * 4", tmp_path)
    assert evaluate_expr(expr, {}) == 14


def test_parentheses_override_precedence(tmp_path):
    """(2 + 3) * 4 should be 20."""
    expr = parse_expr("(2 + 3) * 4", tmp_path)
    assert evaluate_expr(expr, {}) == 20


def test_subtraction_is_left_associative(tmp_path):
    """10 - 3 - 2 should be 5, not 9."""
    expr = parse_expr("10 - 3 - 2", tmp_path)
    assert evaluate_expr(expr, {}) == 5


def test_division_is_left_associative(tmp_path):
    """100 / 5 / 2 should be 10, not 40."""
    expr = parse_expr("100 / 5 / 2", tmp_path)
    assert evaluate_expr(expr, {}) == 10


# ---------- Evaluator: variables & scope ----------

def test_expr_resolves_variable_from_scope(tmp_path):
    expr = parse_expr("k", tmp_path)
    assert evaluate_expr(expr, {"k": 5}) == 5


def test_expr_uses_variable_inside_arithmetic(tmp_path):
    expr = parse_expr("(k * 2 + 1)", tmp_path)
    assert evaluate_expr(expr, {"k": 5}) == 11


def test_expr_undefined_variable_raises(tmp_path):
    expr = parse_expr("unknown_var", tmp_path)
    with pytest.raises(RuntimeError, match="Undefined variable"):
        evaluate_expr(expr, {})


def test_expr_division_by_zero_raises(tmp_path):
    expr = parse_expr("(1 / 0)", tmp_path)
    with pytest.raises(RuntimeError, match="Division by zero"):
        evaluate_expr(expr, {})


def test_expr_none_returns_none(tmp_path):
    """evaluate_expr(None, ...) supports optional fields the user left blank."""
    assert evaluate_expr(None, {}) is None


# ---------- Engine: 'let' execution & scope ----------

def test_execute_let_stores_variable(tmp_path, backend):
    engine = run_program("let k = 5\n", tmp_path, backend)
    assert engine.context.variables["k"] == 5


def test_execute_let_variable_can_use_earlier_variable(tmp_path, backend):
    engine = run_program("let k = 5\nlet m = (k * 2)\n", tmp_path, backend)
    assert engine.context.variables["m"] == 10


def test_execute_let_redefinition_overwrites(tmp_path, backend):
    engine = run_program("let k = 5\nlet k = 9\n", tmp_path, backend)
    assert engine.context.variables["k"] == 9


def test_engine_eval_helper_computes_int(tmp_path, backend):
    engine = run_program("let k = 5\n", tmp_path, backend)
    expr = parse_expr("(k * 2)", tmp_path)
    assert engine.eval(expr) == 10


def test_engine_eval_helper_returns_none_for_missing_optional_field(tmp_path, backend):
    engine = run_program("let k = 5\n", tmp_path, backend)
    assert engine.eval(None) is None


# ---------- Known parser limitation: parenthesize expressions used as step params ----------
# When a step has more than one attribute, an expression with an operator MUST be wrapped in parentheses

def test_unparenthesized_expr_before_another_attribute_fails_to_parse(tmp_path):
    """Known limitation: 'kernel_size=k*2 iterations=1' (no parens) does not parse."""
    program = (
        'load "in.png" as Img\n'
        "let k = 5\n"
        "pipeline P {\n"
        "    erode kernel_size=k*2 iterations=1\n"
        "}\n"
        "apply P to Img\n"
    )
    with pytest.raises(Exception):
        parse(program, tmp_path)


def test_parenthesized_expr_before_another_attribute_parses(tmp_path):
    """Workaround: wrapping the expression in parentheses fixes the ambiguity."""
    program = (
        'load "in.png" as Img\n'
        "let k = 5\n"
        "pipeline P {\n"
        "    erode kernel_size=(k*2) iterations=1\n"
        "}\n"
        "apply P to Img\n"
    )
    model = parse(program, tmp_path)  # should not raise
    assert model.statements[0].__class__.__name__ == "Load"


# ---------- Full pipeline integration: expressions actually driving image processing ----------

def test_full_program_expression_drives_erode_kernel_size(tmp_path, backend, test_binary_image):
    """
    End-to-end: a variable-derived kernel size actually changes the output.
    kernel_size=(k*2+1) with k=1 -> kernel_size=3 (a real, small erosion).
    """
    in_path = str(tmp_path / "in.png")
    out_path = str(tmp_path / "out.png")
    cv2.imwrite(in_path, test_binary_image)

    program = f"""
        let k = 1
        load "{in_path}" as Img
        pipeline P {{
            erode kernel_size=(k*2+1) iterations=(k)
        }}
        apply P to Img
        save Img to "{out_path}"
    """
    run_program(program, tmp_path, backend)

    result = cv2.imread(out_path, cv2.IMREAD_GRAYSCALE)
    assert result is not None
    # erosion shrinks the white square, so it should have fewer white pixels
    assert np.sum(result > 0) < np.sum(test_binary_image > 0)


def test_full_program_expression_with_variable_reused_across_steps(tmp_path, backend, test_binary_image):
    """A single variable can drive multiple step parameters in the same pipeline."""
    in_path = str(tmp_path / "in.png")
    out_path = str(tmp_path / "out.png")
    cv2.imwrite(in_path, test_binary_image)

    program = f"""
        let k = 2
        load "{in_path}" as Img
        pipeline P {{
            dilate kernel_size=(k+1) iterations=(k-1)
            erode kernel_size=(k+1) iterations=(k-1)
        }}
        apply P to Img
        save Img to "{out_path}"
    """
    # should run to completion without raising
    run_program(program, tmp_path, backend)
    assert os.path.exists(out_path)


# ---------- More complex cases: many variables, chains, deep nesting, full multi-step programs ----------

def test_expr_combines_multiple_variables_with_precedence(tmp_path, backend):
    """
    Three independent variables combined in one expression, mixing all four
    operators and precedence: a*b + c/2 - a  with a=3, b=4, c=10
    -> (3*4) + (10/2) - 3 = 12 + 5 - 3 = 14
    """
    engine = run_program("let a = 3\nlet b = 4\nlet c = 10\n", tmp_path, backend)
    expr = parse_expr("(a*b + c/2 - a)", tmp_path)
    result = evaluate_expr(expr, engine.context.variables)
    assert result == 14


def test_expr_variable_chain_depends_on_previous_variables(tmp_path, backend):
    """
    Each variable is defined in terms of the ones before it:
    a = 2
    b = (a + 3)        -> 5
    c = (b * a - 1)     -> 5*2 - 1 = 9
    d = ((c + b) * a)   -> (9+5)*2 = 28
    """
    engine = run_program(
        "let a = 2\n"
        "let b = (a + 3)\n"
        "let c = (b * a - 1)\n"
        "let d = ((c + b) * a)\n",
        tmp_path, backend,
    )
    assert engine.context.variables["b"] == 5
    assert engine.context.variables["c"] == 9
    assert engine.context.variables["d"] == 28


def test_expr_deeply_nested_mixed_operators(tmp_path):
    """
    Stress test for nesting + precedence together:
    (((2 + 3) * (4 - 1)) / (5 - 4)) + ((6 / 2) * (1 + 1))
    -> ((5 * 3) / 1) + (3 * 2)
    -> 15 + 6 = 21
    """
    expr = parse_expr(
        "(((2 + 3) * (4 - 1)) / (5 - 4)) + ((6 / 2) * (1 + 1))", tmp_path
    )
    assert evaluate_expr(expr, {}) == 21


def test_full_program_many_variables_drive_a_multi_step_pipeline(tmp_path, backend, test_binary_image):
    """
    A single pipeline where five different steps are each driven by expressions
    built from a shared set of variables, verifying the whole chain executes
    and actually transforms the image (not just that it doesn't crash).
    """
    in_path = str(tmp_path / "in.png")
    out_path = str(tmp_path / "out.png")
    cv2.imwrite(in_path, test_binary_image)

    program = f"""
        let base = 50
        let scale = 2
        let pad = 5

        load "{in_path}" as Img

        pipeline P {{
            resize width=(base*scale) height=(base*scale)
            crop x=(pad) y=(pad) width=(base*scale - pad*2) height=(base*scale - pad*2)
            cvt_color code=bgr2gray
            threshold value=(base+80) max_value=255 type=binary
            dilate kernel_size=(scale+1) iterations=(1)
            erode kernel_size=(scale+1) iterations=(1)
            canny threshold1=(scale*25) threshold2=(scale*75)
        }}

        apply P to Img
        save Img to "{out_path}"
    """
    run_program(program, tmp_path, backend)

    result = cv2.imread(out_path, cv2.IMREAD_GRAYSCALE)
    assert result is not None
    # resize -> 100x100, then crop removes 5px on each side -> 90x90
    assert result.shape == (90, 90)
    # canny should have produced some edges, i.e. isn't a blank image
    assert np.sum(result > 0) > 0


def test_full_program_shared_variables_across_two_pipelines_and_images(tmp_path, backend, test_binary_image, test_noisy_binary_image):
    """
    Two separate pipelines, applied to two separate images, sharing the same
    global variables - and a variable redefinition between the two 'apply'
    calls should only affect the second one (since 'let' executes in order).
    """
    in_path1 = str(tmp_path / "in1.png")
    in_path2 = str(tmp_path / "in2.png")
    out_path1 = str(tmp_path / "out1.png")
    out_path2 = str(tmp_path / "out2.png")
    cv2.imwrite(in_path1, test_binary_image)
    cv2.imwrite(in_path2, test_noisy_binary_image)

    program = f"""
        let k = 1

        load "{in_path1}" as ImgA
        load "{in_path2}" as ImgB

        pipeline Shrink {{
            erode kernel_size=(k*2+1) iterations=(k)
        }}

        apply Shrink to ImgA
        save ImgA to "{out_path1}"

        let k = 3

        apply Shrink to ImgB
        save ImgB to "{out_path2}"
    """
    engine = run_program(program, tmp_path, backend)
    assert engine.context.variables["k"] == 3

    result_a = cv2.imread(out_path1, cv2.IMREAD_GRAYSCALE)
    result_b = cv2.imread(out_path2, cv2.IMREAD_GRAYSCALE)
    assert result_a is not None and result_b is not None

    # ImgB was eroded with a much larger kernel (k=3 -> size 7) than ImgA (k=1 -> size 3),
    # so it should have lost noticeably more white pixels relative to its own original.
    shrink_a = np.sum(test_binary_image > 0) - np.sum(result_a > 0)
    shrink_b = np.sum(test_noisy_binary_image > 0) - np.sum(result_b > 0)
    assert shrink_b > shrink_a
