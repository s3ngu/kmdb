from api.models import Genre, Movie
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'is_superuser', 'is_staff']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)
    
    def create(self, validated_data):
        user = authenticate(**validated_data)
        token, _ = Token.objects.get_or_create(user=user)
        return {'token': token.key}


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']



class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True)
    class Meta:
        model = Movie
        fields = ['id', 'title', 'duration', 'genres', 'premiere', 'classification', 'synopsis']
    
    def create(self, validated_data):
        genres = validated_data.pop('genres')
        genres = [genre['name'].title() for genre in genres]
        unrepeated_genres = []
        [unrepeated_genres.append({'name': g}) for g in genres if g not in unrepeated_genres]
        movie = Movie.objects.create(**validated_data)
        for genre in [g for g in unrepeated_genres]:
            gr, _ = Genre.objects.get_or_create(**genre)
            movie.genres.add(gr)
        return movie
