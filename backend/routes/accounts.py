from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import BankAccount

accounts_bp = Blueprint("accounts", __name__)

@accounts_bp.route("/api/v1/accounts", methods=["GET"])
@jwt_required()
def list_accounts():
    user_id = get_jwt_identity()
    accounts = BankAccount.query.filter_by(user_id=user_id).all()
    return jsonify({"accounts": [{"id": str(a.id), "account_name": a.account_name, "account_type": a.account_type, "bank_name": a.bank_name, "balance": float(a.balance)} for a in accounts]}), 200

@accounts_bp.route("/api/v1/accounts/<account_id>", methods=["GET"])
@jwt_required()
def get_account(account_id):
    user_id = get_jwt_identity()
    account = BankAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        return jsonify({"error": "Account not found"}), 404
    return jsonify({"id": str(account.id), "account_name": account.account_name, "account_type": account.account_type, "bank_name": account.bank_name, "balance": float(account.balance)}), 200

@accounts_bp.route("/api/v1/accounts", methods=["POST"])
@jwt_required()
def create_account():
    user_id = get_jwt_identity()
    data = request.get_json()
    account = BankAccount(user_id=user_id, account_name=data.get("account_name"), account_number=data.get("account_number"), account_type=data.get("account_type"), bank_name=data.get("bank_name"), balance=float(data.get("balance", 0)), is_active=True)
    db.session.add(account)
    db.session.commit()
    return jsonify({"id": str(account.id), "account_name": account.account_name, "account_type": account.account_type, "bank_name": account.bank_name, "balance": float(account.balance)}), 201
