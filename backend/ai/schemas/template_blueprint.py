TEMPLATE_BLUEPRINT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "document_type",
        "structure",
        "language_grammar",
        "visual_grammar",
        "semantic_slots",
        "rendering_rules",
    ],
    "properties": {
        "document_type": {
            "type": "string",
            "description": (
                "Generic type of legal document represented by the template. "
                "Do not include case-specific names, parties, amounts, dates, "
                "or other instance-specific facts."
            ),
        },

        "structure": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "sections",
                "ordering_rules",
                "numbering",
            ],
            "properties": {
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "order",
                            "id",
                            "title",
                            "purpose",
                            "section_type",
                            "contains",
                            "depends_on",
                        ],
                        "properties": {
                            "order": {
                                "type": "integer",
                            },

                            "id": {
                                "type": "string",
                                "description": (
                                    "Stable generic identifier for this "
                                    "template section."
                                ),
                            },

                            "title": {
                                "type": "string",
                                "description": (
                                    "Generic section title or reusable "
                                    "heading pattern. Do not preserve "
                                    "case-specific facts."
                                ),
                            },

                            "purpose": {
                                "type": "string",
                            },

                            "section_type": {
                                "type": "string",
                            },

                            "contains": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                            },

                            "depends_on": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                            },
                        },
                    },
                },

                "ordering_rules": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },

                "numbering": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "style",
                        "paragraph_numbering",
                        "table_numbering",
                    ],
                    "properties": {
                        "style": {
                            "type": "string",
                        },

                        "paragraph_numbering": {
                            "type": "string",
                        },

                        "table_numbering": {
                            "type": "string",
                        },
                    },
                },
            },
        },

        "language_grammar": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "heading_patterns",
                "paragraph_patterns",
                "clause_patterns",
                "terminology_rules",
            ],
            "properties": {
                "heading_patterns": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },

                "paragraph_patterns": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },

                "clause_patterns": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },

                "terminology_rules": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
            },
        },

        "visual_grammar": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "page_layout",
                "alignment_rules",
                "spacing_rules",
                "indentation_rules",
                "emphasis_rules",
                "table_rules",
                "positioning_rules",
                "page_break_rules",
                "section_break_rules",
            ],
            "properties": {
                "page_layout": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "page_size",
                        "orientation",
                        "margins",
                        "headers",
                        "footers",
                    ],
                    "properties": {
                        "page_size": {
                            "type": ["string", "null"],
                            "description": (
                                "Page size only if explicitly represented "
                                "in the Markdown/Pandoc attributes; "
                                "otherwise null."
                            ),
                        },

                        "orientation": {
                            "type": ["string", "null"],
                            "description": (
                                "Page orientation only if explicitly "
                                "represented in the Markdown/Pandoc "
                                "attributes; otherwise null."
                            ),
                        },

                        "margins": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": [
                                "top",
                                "bottom",
                                "left",
                                "right",
                            ],
                            "properties": {
                                "top": {
                                    "type": ["string", "null"],
                                },

                                "bottom": {
                                    "type": ["string", "null"],
                                },

                                "left": {
                                    "type": ["string", "null"],
                                },

                                "right": {
                                    "type": ["string", "null"],
                                },
                            },
                        },

                        "headers": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },

                        "footers": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                    },
                },

                "alignment_rules": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },

                "spacing_rules": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },

                "indentation_rules": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },

                "emphasis_rules": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },

                "table_rules": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "layout",
                            "borders",
                            "cell_alignment",
                            "header_style",
                            "width_behavior",
                        ],
                        "properties": {
                            "layout": {
                                "type": "string",
                            },

                            "borders": {
                                "type": "string",
                            },

                            "cell_alignment": {
                                "type": "string",
                            },

                            "header_style": {
                                "type": "string",
                            },

                            "width_behavior": {
                                "type": "string",
                            },
                        },
                    },
                },

                "positioning_rules": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },

                "page_break_rules": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },

                "section_break_rules": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
            },
        },

        "semantic_slots": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "slot_id",
                    "slot_type",
                    "description",
                    "section_id",
                    "required",
                    "repetition",
                ],
                "properties": {
                    "slot_id": {
                        "type": "string",
                    },

                    "slot_type": {
                        "type": "string",
                    },

                    "description": {
                        "type": "string",
                    },

                    "section_id": {
                        "type": "string",
                    },

                    "required": {
                        "type": "boolean",
                    },

                    "repetition": {
                        "type": "string",
                    },
                },
            },
        },

        "rendering_rules": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "target",
                    "rule",
                ],
                "properties": {
                    "target": {
                        "type": "string",
                    },

                    "rule": {
                        "type": "string",
                    },
                },
            },
        },
    },
}