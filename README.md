<프로젝트 설명>  
Django DRF를 이용하여 스파르타 뉴스 구현  
-레퍼런스: GeekNews  
---  
<ERD>  

   
1. Accounts,Comments: One-to-Many(1:N)  

   
2. Accounts,Comment_like_users: Many-to-Many(M:N)


3. Accounts,News: One-to-Many(1:N)


4. Accounts,News_like_users: Many-to-Many(M:N)


5. News,Comments: One-to-Many(1:N)


6. News,News_like_users: Many-to-Many(M:N)


7. Comments,Comment_like_users: Many-to-Many(M:N)  


---  
<API 목록>  
- 앱: accounts, news  
   
<accounts 앱>  
- End point: /api/accounts → 회원가입(POST)  
- End point: /api/accounts/login → 로그인(POST)  
- End point: /api/accounts/logout → 로그아웃(POST, 블랙리스트)  
- End point: /api/accounts/<str:username> → 유저 디테일 페이지(GET) , 회원 정보 수정(PUT, 유저네임/password), 회원 탈퇴(DELETE)  
- End point: /api/accounts/<str:username>/my → 내가 작성한 뉴스/댓글 불러오기(GET)  
- End point: /api/accounts/<str:username>/like → 좋아요 누른 뉴스/댓글 불러오기(GET)  
  
<news 앱>  
- End point: /api/news → 뉴스 리스트 가져오기(GET), 뉴스 작성하기(POST)  
- End point: /api/news/<int:newsId> → 뉴스 디테일 페이지(GET), 뉴스 삭제(DELETE), 뉴스 수정(PUT)  
- End point: /api/news/<int:newsId>/like → 뉴스 좋아요(POST), 뉴스 좋아요 삭제(DELETE)  
- End point: /api/news/<int:newsId>/comment → 댓글 목록 보여주기(GET), 댓글 작성하기(POST)  
- End point: /api/news/comment/<int:commentId> → 댓글 보여주기(GET), 댓글 수정하기(PUT), 댓글 삭제하기(DELETE)  
- End point: /api/news/comment/<int:commentId>/like → 댓글 좋아요(POST), 댓글 좋아요 삭제(DELETE)  
- End point: /api/news/latest → 뉴스 최신순 정렬(GET)  
- End point: /api/news/liked → 뉴스 좋아요순 정렬(GET)  
- End point: /api/news/comment → 뉴스 댓글순 정렬(GET)  
- End point: /api/news/search/<str:search> → 뉴스 검색(GET, 제목/내용/url/유저네임)  
- End point: /api/news/comment/search/<str:search> → 댓글 검색(GET, 내용/유저네임)  

*End point가 같은 기능들은 class view로 작성, End point에 기능 1개 → func. view로 작성.  
**추가 기능 구현: 페이지네이션, 팔로우, ...  
