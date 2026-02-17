from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Account

accounts_bp = Blueprint("accounts", __name__)

@accounts_bp.route("/api/v1/accounts", methods=["GET"])
@jwt_required()
def list_accounts():
    user_id = get_jwt_identity()
    accounts = Account.query.filter_by(user_id=user_id).all()
    return jsonify({"accounts": [{"id": str(a.id), "bank_name": a.bank_name, "balance": float(a.balance)} for a in accounts]}), 200

@accounts_bp.route("/api/v1/accounts/<account_id>", methods=["GET"])
@jwt_required()
def get_account(account_id):
    user_id = get_jwt_identity()
    account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        return jsonify({"error": "Account not found"}), 404
    return jsonify({"id": str(account.id), "bank_name": account.bank_name, "balance": float(account.balance)}), 200

@accounts_bp.route("/api/v1/accounts", methods=["POST"])
@jwt_required()
def create_account():
    user_id = get_jwt_identity()
    data = request.get_json()
    account = Account(user_id=user_id, bank_name=data.get("bank_name"), account_number=data.get("account_number"), account_type=data.get("account_type"), balance=float(data.get("balance", 0)), is_active=True)
    db.session.add(account)
    db.session.commit()
    return jsonify({"id": str(account.id), "bank_name": account.bank_name, "balance": float(account.balance)}), 201
