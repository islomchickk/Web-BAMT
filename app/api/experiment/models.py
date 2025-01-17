from ast import literal_eval
from dataclasses import dataclass

from app import db


@dataclass
class BayessianNet(db.Model):
    __tablename__ = 'nets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    owner = db.Column(db.String)
    dataset_name = db.Column(db.String)

    edges = db.Column(db.String, nullable=False)
    nodes = db.Column(db.String, nullable=False)

    has_logit = db.Column(db.Boolean, default=False)
    use_mixture = db.Column(db.Boolean, default=False)
    scoring_function = db.Column(db.String)

    init_nodes = db.Column(db.Text)
    init_edges = db.Column(db.Text)
    # white_list = db.Column(db.Text)
    # bl_add = db.Column(db.Text)
    remove_init_edges = db.Column(db.Boolean, default=False)

    regressor = db.Column(db.String, default="LinearRegression")
    classifier = db.Column(db.String, default="LogisticRegression")

    descriptor = db.Column(db.Text)

    def unpack(self):
        return {"network": {
            "name": self.name,
            "dataset_name": self.dataset_name,
            "edges": literal_eval(self.edges),
            "nodes": literal_eval(self.nodes),
            "use_mixture": self.use_mixture,
            "has_logit": self.has_logit,
            "classifier": self.classifier,
            "regressor": self.regressor,
            "params": {"init_edges": literal_eval(self.init_edges) if self.init_edges else None,
                       "init_nodes": literal_eval(self.init_nodes) if self.init_nodes else None,
                       # "white_list": data.white_list,
                       # "bl_add": data.bl_add,
                       "remove_init_edges": self.remove_init_edges},
            "scoring_function": self.scoring_function,
            "descriptor": literal_eval(self.descriptor)}
        }


@dataclass
class Sample(db.Model):
    __tablename__ = 'samples'
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String)
    net_name = db.Column(db.String)
    dataset_name = db.Column(db.String)

    sample_loc = db.Column(db.String)
    is_default = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Sample(owner={self.owner}, net_name={self.net_name}, dataset_name={self.dataset_name})"
