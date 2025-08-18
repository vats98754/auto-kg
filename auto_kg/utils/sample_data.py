"""
Sample data generator for testing the knowledge graph without Wikipedia access.
"""

import json
from typing import Dict

def generate_sample_math_data() -> Dict:
    """Generate sample mathematical concepts data for testing."""
    
    sample_data = {
        "Linear Algebra": {
            "title": "Linear Algebra",
            "url": "https://en.wikipedia.org/wiki/Linear_algebra",
            "summary": "Linear algebra is the branch of mathematics concerning linear equations, linear maps, and their representations in vector spaces and through matrices. Linear algebra is central to almost all areas of mathematics.",
            "content": "Linear algebra is the branch of mathematics concerning linear equations, linear maps, and their representations in vector spaces and through matrices. Linear algebra is central to almost all areas of mathematics. For instance, linear algebra is fundamental in modern presentations of geometry, including for defining basic objects such as lines, planes and rotations. Also, functional analysis, a branch of mathematical analysis, may be viewed as the application of linear algebra to spaces of functions.",
            "links": ["Vector space", "Matrix", "Linear map", "Eigenvalue", "Determinant", "Functional analysis", "Geometry"],
            "categories": ["Linear algebra", "Abstract algebra", "Mathematical analysis"]
        },
        "Calculus": {
            "title": "Calculus",
            "url": "https://en.wikipedia.org/wiki/Calculus",
            "summary": "Calculus is the mathematical study of continuous change, in the same way that geometry is the study of shape and algebra is the study of generalizations of arithmetic operations.",
            "content": "Calculus is the mathematical study of continuous change, in the same way that geometry is the study of shape and algebra is the study of generalizations of arithmetic operations. It has two major branches, differential calculus and integral calculus. Differential calculus concerns instantaneous rates of change and the slopes of curves. Integral calculus concerns accumulation of quantities and the areas under and between curves.",
            "links": ["Differential calculus", "Integral calculus", "Derivative", "Integral", "Limit", "Analysis"],
            "categories": ["Calculus", "Mathematical analysis", "Differential equations"]
        },
        "Abstract Algebra": {
            "title": "Abstract Algebra",
            "url": "https://en.wikipedia.org/wiki/Abstract_algebra",
            "summary": "In mathematics, abstract algebra is the study of algebraic structures. Algebraic structures include groups, rings, fields, modules, vector spaces, lattices, and algebras.",
            "content": "In mathematics, abstract algebra is the study of algebraic structures. Algebraic structures include groups, rings, fields, modules, vector spaces, lattices, and algebras. The term abstract algebra was coined in the early 20th century to distinguish this area of study from the other parts of algebra.",
            "links": ["Group theory", "Ring theory", "Field theory", "Vector space", "Module", "Lattice"],
            "categories": ["Abstract algebra", "Algebra", "Mathematical structures"]
        },
        "Topology": {
            "title": "Topology",
            "url": "https://en.wikipedia.org/wiki/Topology",
            "summary": "In mathematics, topology is concerned with the properties of a geometric object that are preserved under continuous deformations, such as stretching, twisting, crumpling and bending.",
            "content": "In mathematics, topology is concerned with the properties of a geometric object that are preserved under continuous deformations, such as stretching, twisting, crumpling and bending, but not tearing or gluing. A topological space is a set endowed with a structure, called a topology, which allows defining continuous deformation of subspaces, and, more generally, all kinds of continuity.",
            "links": ["Topological space", "Continuous function", "Homeomorphism", "Homotopy", "Manifold"],
            "categories": ["Topology", "Geometry", "Mathematical analysis"]
        },
        "Number Theory": {
            "title": "Number Theory",
            "url": "https://en.wikipedia.org/wiki/Number_theory",
            "summary": "Number theory is a branch of pure mathematics devoted primarily to the study of the integers and integer-valued functions.",
            "content": "Number theory is a branch of pure mathematics devoted primarily to the study of the integers and integer-valued functions. German mathematician Carl Friedrich Gauss said, 'Mathematics is the queen of the sciences—and number theory is the queen of mathematics.' Number theorists study prime numbers as well as the properties of mathematical objects made out of integers or defined as generalizations of the integers.",
            "links": ["Prime number", "Integer", "Modular arithmetic", "Diophantine equation", "Cryptography"],
            "categories": ["Number theory", "Pure mathematics", "Arithmetic"]
        },
        "Probability Theory": {
            "title": "Probability Theory",
            "url": "https://en.wikipedia.org/wiki/Probability_theory",
            "summary": "Probability theory is the branch of mathematics concerned with probability. Although there are several different probability interpretations, probability theory treats the concept in a rigorous mathematical manner.",
            "content": "Probability theory is the branch of mathematics concerned with probability. Although there are several different probability interpretations, probability theory treats the concept in a rigorous mathematical manner by expressing it through a set of axioms. Typically these axioms formalise probability in terms of a probability space, which assigns a measure taking values between 0 and 1, termed the probability measure, to a set of outcomes called the sample space.",
            "links": ["Probability", "Sample space", "Random variable", "Distribution", "Statistics", "Measure theory"],
            "categories": ["Probability theory", "Statistics", "Measure theory"]
        },
        "Graph Theory": {
            "title": "Graph Theory",
            "url": "https://en.wikipedia.org/wiki/Graph_theory",
            "summary": "In mathematics, graph theory is the study of graphs, which are mathematical structures used to model pairwise relations between objects.",
            "content": "In mathematics, graph theory is the study of graphs, which are mathematical structures used to model pairwise relations between objects. A graph in this context is made up of vertices (also called nodes or points) which are connected by edges (also called links or lines). A distinction is made between undirected graphs, where edges link two vertices symmetrically, and directed graphs, where edges link two vertices asymmetrically.",
            "links": ["Graph", "Vertex", "Edge", "Tree", "Network theory", "Combinatorics"],
            "categories": ["Graph theory", "Combinatorics", "Discrete mathematics"]
        },
        "Real Analysis": {
            "title": "Real Analysis",
            "url": "https://en.wikipedia.org/wiki/Real_analysis",
            "summary": "In mathematics, real analysis is the branch of mathematical analysis that studies the behavior of real numbers, sequences and series of real numbers, and real functions.",
            "content": "In mathematics, real analysis is the branch of mathematical analysis that studies the behavior of real numbers, sequences and series of real numbers, and real functions. Some particular properties of real-valued sequences and functions that real analysis studies include convergence, limits, continuity, smoothness, differentiability and integrability.",
            "links": ["Real number", "Sequence", "Series", "Limit", "Continuity", "Derivative", "Integral"],
            "categories": ["Real analysis", "Mathematical analysis", "Calculus"]
        }
    }
    
    return sample_data

if __name__ == "__main__":
    data = generate_sample_math_data()
    with open("sample_math_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Generated sample data with {len(data)} mathematical concepts")
    print(f"Topics: {list(data.keys())}")