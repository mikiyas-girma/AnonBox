PGDMP         :                |            youbotdb %   14.11 (Ubuntu 14.11-0ubuntu0.22.04.1) %   14.11 (Ubuntu 14.11-0ubuntu0.22.04.1) $    :           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            ;           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            <           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            =           1262    25076    youbotdb    DATABASE     ]   CREATE DATABASE youbotdb WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.UTF-8';
    DROP DATABASE youbotdb;
                mikias    false            �            1259    25133    admin_messages    TABLE     k   CREATE TABLE public.admin_messages (
    user_message_id integer NOT NULL,
    admin_message_id integer
);
 "   DROP TABLE public.admin_messages;
       public         heap    mikias    false            �            1259    25132 "   admin_messages_user_message_id_seq    SEQUENCE     �   CREATE SEQUENCE public.admin_messages_user_message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 9   DROP SEQUENCE public.admin_messages_user_message_id_seq;
       public          mikias    false    216            >           0    0 "   admin_messages_user_message_id_seq    SEQUENCE OWNED BY     i   ALTER SEQUENCE public.admin_messages_user_message_id_seq OWNED BY public.admin_messages.user_message_id;
          public          mikias    false    215            �            1259    25116 	   questions    TABLE       CREATE TABLE public.questions (
    question_id bigint NOT NULL,
    user_id bigint NOT NULL,
    question character varying NOT NULL,
    category character varying NOT NULL,
    status character varying NOT NULL,
    username character varying NOT NULL
);
    DROP TABLE public.questions;
       public         heap    mikias    false            �            1259    25115    questions_question_id_seq    SEQUENCE     �   CREATE SEQUENCE public.questions_question_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.questions_question_id_seq;
       public          mikias    false    212            ?           0    0    questions_question_id_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE public.questions_question_id_seq OWNED BY public.questions.question_id;
          public          mikias    false    211            �            1259    25126    states    TABLE     �   CREATE TABLE public.states (
    user_id bigint NOT NULL,
    question_type character varying(50) NOT NULL,
    category character varying(50) NOT NULL,
    timeframe character varying(50) NOT NULL
);
    DROP TABLE public.states;
       public         heap    mikias    false            �            1259    25125    states_user_id_seq    SEQUENCE     {   CREATE SEQUENCE public.states_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.states_user_id_seq;
       public          mikias    false    214            @           0    0    states_user_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE public.states_user_id_seq OWNED BY public.states.user_id;
          public          mikias    false    213            �            1259    25078    users    TABLE     �   CREATE TABLE public.users (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    username character varying,
    first_name character varying,
    last_name character varying
);
    DROP TABLE public.users;
       public         heap    mikias    false            �            1259    25077    users_id_seq    SEQUENCE     �   CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.users_id_seq;
       public          mikias    false    210            A           0    0    users_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
          public          mikias    false    209            �           2604    25136    admin_messages user_message_id    DEFAULT     �   ALTER TABLE ONLY public.admin_messages ALTER COLUMN user_message_id SET DEFAULT nextval('public.admin_messages_user_message_id_seq'::regclass);
 M   ALTER TABLE public.admin_messages ALTER COLUMN user_message_id DROP DEFAULT;
       public          mikias    false    216    215    216            �           2604    25119    questions question_id    DEFAULT     ~   ALTER TABLE ONLY public.questions ALTER COLUMN question_id SET DEFAULT nextval('public.questions_question_id_seq'::regclass);
 D   ALTER TABLE public.questions ALTER COLUMN question_id DROP DEFAULT;
       public          mikias    false    211    212    212            �           2604    25129    states user_id    DEFAULT     p   ALTER TABLE ONLY public.states ALTER COLUMN user_id SET DEFAULT nextval('public.states_user_id_seq'::regclass);
 =   ALTER TABLE public.states ALTER COLUMN user_id DROP DEFAULT;
       public          mikias    false    214    213    214            �           2604    25081    users id    DEFAULT     d   ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
 7   ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT;
       public          mikias    false    209    210    210            7          0    25133    admin_messages 
   TABLE DATA           K   COPY public.admin_messages (user_message_id, admin_message_id) FROM stdin;
    public          mikias    false    216   <'       3          0    25116 	   questions 
   TABLE DATA           _   COPY public.questions (question_id, user_id, question, category, status, username) FROM stdin;
    public          mikias    false    212   �'       5          0    25126    states 
   TABLE DATA           M   COPY public.states (user_id, question_type, category, timeframe) FROM stdin;
    public          mikias    false    214   ,       1          0    25078    users 
   TABLE DATA           Q   COPY public.users (id, telegram_id, username, first_name, last_name) FROM stdin;
    public          mikias    false    210   [,       B           0    0 "   admin_messages_user_message_id_seq    SEQUENCE SET     Q   SELECT pg_catalog.setval('public.admin_messages_user_message_id_seq', 1, false);
          public          mikias    false    215            C           0    0    questions_question_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.questions_question_id_seq', 1, false);
          public          mikias    false    211            D           0    0    states_user_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.states_user_id_seq', 1, false);
          public          mikias    false    213            E           0    0    users_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.users_id_seq', 4, true);
          public          mikias    false    209            �           2606    25138 "   admin_messages admin_messages_pkey 
   CONSTRAINT     m   ALTER TABLE ONLY public.admin_messages
    ADD CONSTRAINT admin_messages_pkey PRIMARY KEY (user_message_id);
 L   ALTER TABLE ONLY public.admin_messages DROP CONSTRAINT admin_messages_pkey;
       public            mikias    false    216            �           2606    25123    questions questions_pkey 
   CONSTRAINT     _   ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (question_id);
 B   ALTER TABLE ONLY public.questions DROP CONSTRAINT questions_pkey;
       public            mikias    false    212            �           2606    25131    states states_pkey 
   CONSTRAINT     U   ALTER TABLE ONLY public.states
    ADD CONSTRAINT states_pkey PRIMARY KEY (user_id);
 <   ALTER TABLE ONLY public.states DROP CONSTRAINT states_pkey;
       public            mikias    false    214            �           2606    25085    users users_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            mikias    false    210            �           2606    25087    users users_telegram_id_key 
   CONSTRAINT     ]   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_telegram_id_key UNIQUE (telegram_id);
 E   ALTER TABLE ONLY public.users DROP CONSTRAINT users_telegram_id_key;
       public            mikias    false    210            �           1259    25124    ix_questions_question_id    INDEX     U   CREATE INDEX ix_questions_question_id ON public.questions USING btree (question_id);
 ,   DROP INDEX public.ix_questions_question_id;
       public            mikias    false    212            �           1259    25088    ix_users_id    INDEX     ;   CREATE INDEX ix_users_id ON public.users USING btree (id);
    DROP INDEX public.ix_users_id;
       public            mikias    false    210            �           1259    25089    ix_users_username    INDEX     N   CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);
 %   DROP INDEX public.ix_users_username;
       public            mikias    false    210            7   Y   x�̱�0B�Z��	�Kd��?Gpw�&� [m��gV)����,C�����H<��2pؑ��2��vU�Gc�����. ?up;      3   ]  x��X]n�F~�O���pw��q� m�r� }aĵ��$R����B{��#w��.��A����7���i��H�I�	���!>F���>�uT�Ca��>?l�C}�Y�D*�R�T���8D+�.ծڜ�u6��.��Y�yI�M��>��E�z�w�:�������}�+z<>#ϣO:�u��`J�u�J�]�d*�o3k�z>�8A�$���5ݶS_xbyߝ�n�������)��/�I�q��n��G�Z�}ĳ��p� 2��i�NX�N������
+@F_����z�;�R�U�Bh����a�g>a8<J��w���D`8�Å���
bDJM��
SB�߉�U^8%�S?�b�1�3��⺿m��	��!�RJq�"�T���X,uU�=q$�;:���9�M�xm(�:�9�f��C���=�<iVkS�_�N�]�w��ch�q�/M|�a�\����7e|��Z�{��К�7�ٿ|�L�+�������^�����\��rkcPr6�sc
�L	���m�#��M�u	a�$Ű�?�vX�7��SCU��G���G��zf9Es���7sc��3����1�FXΊ��<���5{�k�nU��u<�?	�2��"p7��p�oA틾��ί�u�
`Ur�%Y�L�����f���$�B��9a-?�1&��j��!)�����w�I���XY��Z�+�'�L��e���߫n���);?�l/�\@gv�D��$�h�}��K� v����Ͽ8`����ZJ�i�j�.�i#Օ���_�灳,s��Jd��P�,
�ι@�P|���yU��7<	��.�.�^B�g
�ȟ�_w�$��ߞZ~�P��d�Z����3�fjg짞�/R�Q�Zf6����b�5P(�<�5>k�J^��۝e����M�},&�}�
~�4s8ܟ`P�y�_&�U���e�$���x�f��{\�@��.�k��(�2�	�������?!�	ɱ���&�=�>6��oH�``�C�hd�Π�: p;ÿ�N'_7�<s��/9q�	�L1����lC�+�EᕳJ����,5%���w�+�y]7�	ǆ�s��	#��G��oonn�wj,�      5   9   x�3�01127651��K�+.O-JM�IM���OI��2�4333�03�!���� �i$      1   �   x�3�4�4333�03���L�H�04��0�u� �Y�&O���242"N#c##�������T0]ə�X\b������r����@tiq�	��P�����gPb^zjh�/�7W� �1*�     